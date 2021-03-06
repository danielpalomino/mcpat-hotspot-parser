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

#READ ALL LINES OF FILE
def get_lines_of_file(fin):
	all_lines = fin.read()
	fin.close()
	return all_lines

#GET NUMBER OF ELEMENTS BASED ON DE "elem" re object.
#elem = regular expression object for number of elements (core, l2, etc...)
#all_lines = the file
def get_number_of_elems(elem, all_lines):
	m = elem.search(all_lines)
	if m:
		return int(m.group(1))
	else:
		return 1

#GET LIST OF POWER TRACES. THE LIST CONTAINS LISTS OF POWER TRACES FOR ALL ELEMENTS OF THE SAME TYPE (ex: core0, core1, ..., coren)
#elem = regular expression object for attributes of element "elem"
def get_power_traces(elem, number_of_elems, all_lines):
	p_traces = []
	for n in range(0,number_of_elems):
		p_traces.append([])
		
	traces_list = elem.findall(all_lines)
	for i in range(0,len(traces_list)):
		p_traces[i%number_of_elems].append(traces_list[i][4]);
	return p_traces

#WRITE HEADER TO PTRACE FILE (ONLY CORES AND L2S FOR NOW)
def write_header_ptrace(fout,number_of_cores,number_of_l2s):
	#WRITE CORES HEADERS
	for i in range(0,number_of_cores):
		fout.write('Core_'+str(i)+'\t')
	#WRITE L2s HEADERS
	for i in range(0,number_of_l2s):
		fout.write('L2_'+str(i)+'\t')
	#WRITE NEW LINE
	fout.write('\n')

#WRITE POWER TRACES TO PTRACE FILE (ONLY CORES AND L2S FOR NOW)
def write_traces_ptrace(fout,number_of_traces,p_traces_cores,p_traces_l2s):
	for i in range(0,number_of_traces):
		#write cores traces
		for j in range(0,len(p_traces_cores)):
			fout.write(p_traces_cores[j][i] + '\t')
		#write l2s traces
		for j in range(0,len(p_traces_l2s)):
			fout.write(p_traces_l2s[j][i] + '\t')	
		fout.write('\n')

#n_increase = number of times that the traces will be increased
def artificial_sim_increase(p_traces,number_of_traces,n_increase):
	for i in range(0,n_increase):
		for j in range(0,len(p_traces)):
			last_trace = p_traces[j][-1]
			#increase traces
			for k in range(0,number_of_traces):
				p_traces[j].append(str(float(p_traces[j][k])+float(last_trace)))
	

#OPEN MCPAT LOG
fin = open(sys.argv[1],'r')

all_lines = get_lines_of_file(fin)

number_of_cores = get_number_of_elems(ncores,all_lines)

number_of_l2s = get_number_of_elems(nl2s,all_lines)

p_traces_cores = get_power_traces(core,number_of_cores,all_lines)

p_traces_l2s = get_power_traces(l2,number_of_l2s,all_lines)


#print p_traces_cores[0]
#print p_traces_l2s

#MAKE SURE THE NUMBER OF TRACES ARE OK
assert len(p_traces_cores[0]) == len(p_traces_l2s[0])

artificial_sim_increase(p_traces_cores,len(p_traces_cores[0]),3)
artificial_sim_increase(p_traces_l2s,len(p_traces_l2s[0]),3)


#GET NUMBER OF TRACES
number_of_traces = len(p_traces_cores[0])

#WRITE TRACES TO P_TRACE FILE
ptrace_file_name = sys.argv[1].split('.')
fout = open(ptrace_file_name[0]+'.ptrace','w')

#WRITE HEADER TO PTRACE FILE
write_header_ptrace(fout,number_of_cores,number_of_l2s)

#WRITE POWER TRACES
write_traces_ptrace(fout,number_of_traces,p_traces_cores,p_traces_l2s)

fout.close()


