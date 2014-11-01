import re
import sys

#regular expressions
ncores = re.compile('Total Cores: (\d+) cores')
nl2s = re.compile('Total L2s: (\d+)')
re_core = 'Core:\n'
re_l2 = 'L2\n'

re_area = '\s*Area\s*=\s*([0-9.]*)\s*\w*\^\w*\n'
re_peak = '\s*Peak\s*Dynamic\s*=\s*([0-9.]*)\s*\w*\n'
re_subth = '\s*Subthreshold\s*Leakage\s*=\s*([0-9.]*)\s*\w*\n'
re_gate = '\s*Gate\s*Leakage\s*=\s*([0-9.]*)\s*\w*\n'
re_run = '\s*Runtime\s*Dynamic\s*=\s*([0-9.]*)\s*\w*\n'

core = re.compile(re_core+re_area+re_peak+re_subth+re_gate+re_run)
l2 = re.compile(re_l2+re_area+re_peak+re_subth+re_gate+re_run)

#OPEN MCPAT LOG
fin = open(sys.argv[1],'r')

number_of_cores = 1
number_of_l2s = 1

#READ ALL LINES OF FILE
all_lines = fin.read()
fin.close()

m = ncores.search(all_lines)
if m:
	number_of_cores = int(m.group(1))

m = nl2s.search(all_lines)
if m:
	number_of_l2s = int(m.group(1))

#LIST OF LISTS OF POWER TRACES FOR ALL CORES
p_traces_cores = []
for n in range(0,number_of_cores):
	p_traces_cores.append([])


#LIST OF LISTS OF POWER TRACES FOR ALL L2s
p_traces_l2s = []
for n in range(0,number_of_l2s):
	p_traces_l2s.append([])


#FIND ALL CORES TRACES. EACH TRACE IS A 5-TUPLE: (0) AREA, (1) PEAK_DYNAMIC, (2) SUBTHRESHOLD, (3) GATE LEAKAGE, (4) RUN TIME DYNAMIC
cores_traces_list = core.findall(all_lines)

for i in range(0,len(cores_traces_list)):
	p_traces_cores[i%number_of_cores].append(cores_traces_list[i][4]);

print p_traces_cores

#FIND ALL l2s TRACES. EACH TRACE IS A 5-TUPLE: (0) AREA, (1) PEAK_DYNAMIC, (2) SUBTHRESHOLD, (3) GATE LEAKAGE, (4) RUN TIME DYNAMIC
l2s_traces_list = l2.findall(all_lines)
for i in range(0,len(l2s_traces_list)):
	p_traces_l2s[i%number_of_l2s].append(l2s_traces_list[i][4]);

#print
#print p_traces_l2s

#MAKE SURE THE NUMBER OF TRACES ARE OK
assert len(cores_traces_list)/number_of_cores == len(l2s_traces_list)/number_of_l2s

number_of_traces = len(cores_traces_list)/number_of_cores

#WRITE TRACES TO P_TRACE FILE
ptrace_file_name = sys.argv[1].split('.')
fout = open(ptrace_file_name[0]+'.ptrace','w')

#WRITE HEADER TO PTRACE FILE
#WRITE CORES HEADERS
for i in range(0,number_of_cores):
	fout.write('Core_'+str(i)+'\t')
#WRITE L2s HEADERS
for i in range(0,number_of_l2s):
	fout.write('L2_'+str(i)+'\t')
#WRITE NEW LINE
fout.write('\n')

#WRITE POWER TRACES
for i in range(0,number_of_traces):
	#write cores traces
	for j in range(0,len(p_traces_cores)):
		fout.write(p_traces_cores[j][i] + '\t')
	#write l2s traces
	for j in range(0,len(p_traces_l2s)):
		fout.write(p_traces_l2s[j][i] + '\t')	
	fout.write('\n')

fout.close()


