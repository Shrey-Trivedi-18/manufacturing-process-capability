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
    row['Status'] += ' - PROVISIONAL; TREND DISCREPANCY OPEN' if analysis == 'verification'
  else
    row['Minitab'] = row['Difference'] = nil
    row['Status'] = analysis == 'ANOVA' ? 'NOT RUN - OUTSIDE REQUESTED THREE ANALYSES' : 'CHART RUN - FULL-PRECISION LIMIT COMPARISON NOT TABULATED'
  end
end
CSV.open(comparison_path, 'w') { |csv| csv << comparison.headers; comparison.each { |row| csv << row } }
