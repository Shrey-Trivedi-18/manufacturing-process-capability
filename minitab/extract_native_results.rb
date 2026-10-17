# Extract saved Minitab results; this script does not perform statistical analyses.
# Usage: ruby minitab/extract_native_results.rb minitab/outputs/shaft_quality.mpx
require 'json'
require 'csv'
require 'fileutils'

archive = File.expand_path(ARGV.fetch(0))
output = File.dirname(archive)
def read_member(archive, member)
  JSON.parse(IO.popen(['unzip', '-p', archive, member], &:read))
end
def tables_in(value, found = [])
  case value
  when Hash
    found << value if value['TableCol']
    value.each_value { |child| tables_in(child, found) }
  when Array
    value.each { |child| tables_in(child, found) }
  end
  found
end
metadata = read_member(archive, '/project_metadata_20.json')
manifest = []
ndc = nil
metadata.fetch('Commands').fetch('Items').each_with_index do |command, index|
  stem = format('%02d', index + 1)
  # Command history is the original Minitab-generated specification, not recreated commands.
  File.write(File.join(output, "#{stem}_commands.txt"), command.fetch('CommandLines').map { |line| line['Original'] }.join)
  command.fetch('OutputGroups').each do |group|
    native = read_member(archive, group.fetch('Uri') + '.json')
    visit = lambda do |value|
      case value
      when Hash
        if value['Base'] == 'Number of Distinct Categories = %1'
          ndc = value.fetch('SentenceValues').first.fetch('Value').fetch('Value')
        end
        value.each_value { |child| visit.call(child) }
      when Array
        value.each { |child| visit.call(child) }
      end
    end
    visit.call(native)
    tables_in(native).each_with_index do |table, table_index|
      title = (table['Titles'] || []).map { |x| x.dig('Value', 'Base') }.compact.join(' ')
      title = table['Tag'].to_s if title.empty?
      columns = table.fetch('TableCol').map { |x| x.fetch('Value') }
      headers = columns.map do |column|
        labels = (column['UnformattedLabels'] || []).map { |x| x['Label'] }.compact
        labels.empty? ? column['Tag'] : labels.join(' ')
      end
      values = columns.map do |column|
        raw = column['Values'] || (column['StringValues'] || []).map { |x| x.dig('Value', 'Base') }
        # Minitab's numeric missing sentinel is not a measured or estimated value.
        raw.map { |value| value == 1.23456e30 ? nil : value }
      end
      name = "#{stem}_table_#{table_index + 1}.csv"
      CSV.open(File.join(output, name), 'w') do |csv|
        csv << headers
        (values.map(&:length).max || 0).times { |row| csv << values.map { |column| column[row] } }
      end
      manifest << {command: index + 1, title: group['Title'], table: title, file: name, executed: command['Executed']}
    end
  end
end
File.write(File.join(output, 'table_manifest.json'), JSON.pretty_generate(manifest) + "\n")
puts JSON.pretty_generate(manifest)

# Compare saved outputs with the pre-existing reference, without redoing the analyses.
read_table = ->(name) { CSV.read(File.join(output, name), headers: true) }
components = read_table.call('01_table_2.csv')
evaluation = read_table.call('01_table_3.csv')
process = read_table.call('04_table_1.csv')
overall = read_table.call('04_table_2.csv')
within = read_table.call('04_table_3.csv')
sheet = read_member(archive, '/sheets/1/sheet.json')
stored = sheet.fetch('Data').fetch('Columns').to_h do |column|
  [column.dig('VarId', 'VarId'), column.dig('WorksheetVarBody', 'VarData', 'VarDataBody')]
end
numeric = ->(column) { stored.fetch(column).fetch('NumericData') }
# Check data integrity, not statistical outcomes: the imported measurements must be untouched.
source = CSV.read(File.join(File.dirname(output), '..', 'phase2_spc_capability', 'spc_data.csv'), headers: true)
raise 'Shaft measurements changed' unless numeric.call(8) == source.map { |row| row['Diameter_mm'].to_f }
raise 'Subgroup identifiers changed' unless numeric.call(2) == source.map { |row| row['Subgroup'].to_f }
chart_columns = { 'Mean'=>20, 'Range'=>21, 'Center'=>22, 'R_Center'=>23,
                  'X_LCL'=>24, 'X_UCL'=>25, 'R_LCL'=>26, 'R_UCL'=>27 }
CSV.open(File.join(output, 'control_chart_statistics.csv'), 'w') do |csv|
  csv << ['Subgroup', *chart_columns.keys]
  140.times { |index| csv << [index + 1, *chart_columns.values.map { |column| numeric.call(column)[index] }] }
end
calibration_cases = [
  ['Eight increasing values', 6, '11_table_1.csv', [7, 8]],
  ['Six increasing values', 5, '12_table_1.csv', [6]],
  ['Six decreasing values', 5, '12_table_2.csv', [6]]
]
CSV.open(File.join(output, 'calibration_checks.csv'), 'w') do |csv|
  csv << ['Diagnostic', 'Native_K', 'Observed_alarm_points', 'Evidence']
  calibration_cases.each do |name, k, file, expected|
    text = CSV.read(File.join(output, file), headers: true).map { |row| row[0].to_s }.find { |line| line.include?('Test Failed at points:') }
    actual = text.sub(/.*Test Failed at points:\s*/m, '').scan(/\d+/).map(&:to_i)
    raise "Calibration evidence changed: #{name}" unless actual == expected
    csv << [name, k, actual.join(' '), file]
  end
  negative_index = metadata.fetch('Commands').fetch('Items').index do |command|
    command['CommandLines'].any? { |line| line['Original'].include?('Diagnostic Negative Controls') }
  end
  raise 'Negative-control run missing' unless negative_index
  raise 'Unexpected negative-control alarm table' if manifest.any? { |entry| entry[:command] == negative_index + 1 }
  ['Tie breaks trend', 'Reversal breaks trend', 'Five valid points do not trigger'].each do |name|
    csv << [name, 5, 'none reported', "native command #{negative_index + 1}"]
  end
end
limit_values = {}
{'reference_limits'=>0, 'new_limits'=>60}.each do |name, index|
  limit_values[name] = {'center'=>numeric.call(22)[index], 'rbar'=>numeric.call(23)[index],
    'x_lcl'=>numeric.call(24)[index], 'x_ucl'=>numeric.call(25)[index],
    'r_lcl'=>numeric.call(26)[index], 'r_ucl'=>numeric.call(27)[index],
    'sigma_within'=>numeric.call(29)[name == 'reference_limits' ? 0 : 1]}
end
# Read Minitab's final stored alarm table; never derive alarms from the measurements here.
final_command_index = metadata.fetch('Commands').fetch('Items').index do |command|
  command['CommandLines'].any? { |line| line['Original'].include?('Matched Run Boundaries') }
end
raise 'Corrected chart is missing' unless final_command_index
final_table = manifest.find { |entry| entry[:command] == final_command_index + 1 && entry[:table].include?('Test Results for Xbar') }
alarms = {}
current_test = nil
CSV.read(File.join(output, final_table.fetch(:file)), headers: true).each do |row|
  text = row[0].to_s
  current_test = "T#{Regexp.last_match(1)}" if text =~ /TEST (\d)\./
  alarms[current_test] = text.sub(/.*Test Failed at points:\s*/m, '').scan(/\d+/).map(&:to_i) if text.include?('Test Failed at points:')
end
reference_alarms = CSV.read(File.join(File.dirname(output), '..', 'phase2_spc_capability', 'alarm_log.csv'), headers: true)
CSV.open(File.join(output, 'alarm_comparison.csv'), 'w') do |csv|
  csv << ['Test', 'Reference_subgroups', 'Minitab_subgroups', 'Status']
  %w[T1 T2 T3].each do |test|
    expected = reference_alarms.select { |row| row['X_Rules'].to_s.split(',').include?(test) }.map { |row| row['Subgroup'].to_i }
    actual = alarms.fetch(test, [])
    raise "Alarm mismatch for #{test}" unless expected == actual
    csv << [test, expected.join(' '), actual.join(' '), 'EXACT ALARM LIST MATCH - CALIBRATED CONFIGURATION']
  end
end
find_row = ->(table, value) { table.find { |row| row[0] == value } }
grr = {}
{'repeatability_var'=>'Repeatability', 'operator_var'=>'Operator', 'interaction_var'=>'Operator*Part_ID',
 'part_var'=>'Part-To-Part', 'grr_var'=>'Total Gage R&R'}.each do |metric, source|
  grr[metric] = find_row.call(components, source)[1].to_f
end
grr_row = find_row.call(evaluation, 'Total Gage R&R')
grr.merge!('grr_sd'=>grr_row[1].to_f, 'percent_study_variation'=>grr_row[3].to_f,
           'percent_tolerance'=>grr_row[4].to_f, 'ndc'=>ndc)
comparison_path = File.join(File.dirname(output), 'comparison.csv')
comparison = CSV.read(comparison_path, headers: true)
comparison.each do |row|
  analysis, metric = row['Analysis'], row['Metric']
  value = if analysis == 'GRR'
    grr[metric]
  elsif limit_values[analysis]
    limit_values[analysis][metric]
  elsif %w[reference rebaseline verification setup_shift].include?(analysis)
    table, key = case metric
    when 'mean' then [process, 'Sample Mean']
    when 'within_sd' then [process, 'StDev(Within)']
    when 'overall_sd' then [process, 'StDev(Overall)']
    when 'Cp', 'Cpk' then [within, metric]
    when 'Pp', 'Ppk' then [overall, metric]
    end
    find_row.call(table, analysis)[key].to_f if table
  end
  if value
    difference = value - row['Python'].to_f
    tolerance = metric.end_with?('_var') ? 1e-7 : (%w[Cp Cpk Pp Ppk].include?(metric) ? 0.002 : 1e-5)
    row['Minitab'], row['Difference'] = value, difference
    row['Status'] = difference.abs <= tolerance ? 'MATCH WITHIN TOLERANCE' : 'REVIEW DIFFERENCE'
    row['Status'] += ' - PROVISIONAL; TREND CONFIRMED IN BOTH TOOLS' if analysis == 'verification'
    row['Status'] = 'EXPLAINED CONSTANT PRECISION DIFFERENCE; SAME ALARM OUTCOME' if metric == 'r_ucl' && limit_values[analysis]
    row['Status'] += ' - SUPPLIED HISTORICAL PARAMETER' if limit_values[analysis] && %w[center sigma_within].include?(metric)
  else
    row['Minitab'] = row['Difference'] = nil
    row['Status'] = analysis == 'ANOVA' ? 'NOT RUN - OUTSIDE REQUESTED THREE ANALYSES' : 'CHART RUN - FULL-PRECISION LIMIT COMPARISON NOT TABULATED'
  end
end
CSV.open(comparison_path, 'w') { |csv| csv << comparison.headers; comparison.each { |row| csv << row } }
