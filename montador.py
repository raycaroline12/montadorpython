
import json  
import re
import sys

#os dados em binario das instruções e dos registradores estão contidos num dicionario json
dicionario_instructions_registers = open('dicionario.json', 'r')
dicionario_instructions_registers = dicionario_instructions_registers.read()
dicionariojson = json.loads(dicionario_instructions_registers) 

#vamos receber o arquivo de entrada .asm como argumento no terminal
arquivo = sys.argv[1]

#ler codigo .asm
assemblyCode = open(arquivo, 'r')
assemblyCode = assemblyCode.read()

def tratarCodigo(file):
        text = re.sub('#.+', '', file, flags=re.MULTILINE).strip() #remover comentários
        text = re.sub('\(', ',', text, flags=re.MULTILINE) #trocar '(' por ','
        text = re.sub('\)', '', text, flags=re.MULTILINE) #remover ')'
        text = re.sub('\t', '', text, flags=re.MULTILINE) #remover tab
        return text

def removerLinhasBranco(code):
        lines = code.splitlines()
        lines = filter(None, lines)
        text = '\n'.join(lines)
        return text

def armazenarLabels(code):
        labels = re.findall('.+:', code, re.MULTILINE)
        i=0
        for element in labels:
                labels[i]= re.sub('\:', '', element)
                i += 1  
        return labels

def armazenarPosiçãoLabels(code):
        code_lines = code.splitlines()
        labels_positions = []
        cont=0
        for line in code_lines:
                if line[-1]==':': #verifica se a label está sozinha na linha
                        labels_positions.append(cont) #pega a próxima posição (posição da instrução)
                elif re.search('.+:', line):
                        labels_positions.append(cont)
                        cont +=1
                else:
                        cont+=1
        return labels_positions

def gerarDicionarioLabels(list1, list2):
        dicionario_labels = {}
        for i in range(len(list1)):
                dicionario_labels[list1[i]] = list2[i]
        return dicionario_labels

def removerLabels(code):
        code = re.sub('.+:', '', code, flags=re.MULTILINE)
        code = removerLinhasBranco(code)
        return code

def armazenarLinhasDeInstruções(code):
        lines = code.splitlines()
        list_of_lines = []
        for line in lines:
                line = re.split('[\s+,]', line)
                line = list(filter(None, line))
                list_of_lines.append(line)
        return list_of_lines

def converterNegativoParaBinario(number):
	index = flag = 0
	number = number[::-1]
	new_number = ''
	while index < len(number):
		if number[index] == '1' and flag ==0:
			flag = 1
			new_number = number[index] + new_number
		elif number[index] == '1' and flag ==1:
			new_number = '0' + new_number
		elif number[index] == '0' and flag == 1:
			new_number = '1' + new_number
		else:
			new_number = number[index] + new_number
		index+=1
	return new_number

def converterCodigoParaBinario(list, dicionario_de_labels):
        list_of_bin = []
        for pc, line in enumerate(list):
                if dicionariojson['instructions'][line[0]]['type']=='R':
                        bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[2]]['bin'] + dicionariojson['registers'][line[3]]['bin'] + dicionariojson['registers'][line[1]]['bin'] + dicionariojson['instructions'][line[0]]['shamt'] + dicionariojson['instructions'][line[0]]['funct']
                        list_of_bin.append(bin_line)
                elif dicionariojson['instructions'][line[0]]['type']=='R_jr':
                        bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[1]]['bin'] + dicionariojson['registers']['$zero']['bin'] + dicionariojson['registers']['$zero']['bin'] + dicionariojson['instructions'][line[0]]['shamt'] + dicionariojson['instructions'][line[0]]['funct']
                        list_of_bin.append(bin_line)
                elif dicionariojson['instructions'][line[0]]['type']=='R_shift':
                        num = int(line[3])
                        codbin = bin(num)[2:].zfill(5)
                        shamt = str(codbin)
                        bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers']['$zero']['bin'] + dicionariojson['registers'][line[2]]['bin'] + dicionariojson['registers'][line[1]]['bin'] + shamt + dicionariojson['instructions'][line[0]]['funct']
                        list_of_bin.append(bin_line)
                elif dicionariojson['instructions'][line[0]]['type']=='I':
                        num = int(line[3])
                        if num < 0:
                                negativo = abs(num)
                                negativo = bin(negativo)[2:].zfill(16)
                                negativo = str(negativo)
                                immediate = converterNegativoParaBinario(negativo)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[1]]['bin'] + dicionariojson['registers'][line[2]]['bin'] + immediate
                                list_of_bin.append(bin_line)
                        else:
                                positivo = bin(num)[2:].zfill(16)
                                immediate = str(positivo)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[1]]['bin'] + dicionariojson['registers'][line[2]]['bin'] + immediate
                                list_of_bin.append(bin_line)
                elif dicionariojson['instructions'][line[0]]['type']=='I_lui':
                        num = int(line[2])
                        if num < 0:
                                negativo = abs(negativo)
                                negativo = bin(negativo)[2:].zfill(16)
                                negativo = str(negativo)
                                immediate = converterNegativoParaBinario(negativo)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers']['$zero']['bin'] + dicionariojson['registers'][line[1]]['bin'] + immediate
                                list_of_bin.append(bin_line)
                        else:
                                positivo = bin(num)[2:].zfill(16)
                                immediate = str(positivo)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers']['$zero']['bin'] + dicionariojson['registers'][line[1]]['bin'] + immediate
                                list_of_bin.append(bin_line)
                elif dicionariojson['instructions'][line[0]]['type']=='I_w':
                        num = int(line[2])
                        if num < 0:
                                negativo = abs(num)
                                negativo = bin(negativo)[2:].zfill(16)
                                negativo = str(negativo)
                                immediate = converterNegativoParaBinario(negativo)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[3]]['bin'] + dicionariojson['registers'][line[1]]['bin'] + immediate
                                list_of_bin.append(bin_line)
                        else:
                                positivo = bin(num)[2:].zfill(16)
                                immediate = str(positivo)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[3]]['bin'] + dicionariojson['registers'][line[1]]['bin'] + immediate
                                list_of_bin.append(bin_line)
                elif dicionariojson['instructions'][line[0]]['type']=='I_b':
                        address = dicionario_de_labels[line[3]] - (pc +1)
                        if address < 0:
                                address = abs(address)
                                address = bin(address)[2:].zfill(16)
                                address = str(address)
                                offset = converterNegativoParaBinario(address)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[1]]['bin'] + dicionariojson['registers'][line[2]]['bin'] + offset
                                list_of_bin.append(bin_line)
                        else:
                                address = bin(address)[2:].zfill(16)
                                offset = str(address)
                                bin_line = dicionariojson['instructions'][line[0]]['op'] + dicionariojson['registers'][line[1]]['bin'] + dicionariojson['registers'][line[2]]['bin'] + offset
                                list_of_bin.append(bin_line)               
                elif dicionariojson['instructions'][line[0]]['type']=='J':
                        address = bin(dicionario_de_labels[line[1]])[2:].zfill(26)
                        address = str(address)
                        bin_line = dicionariojson['instructions'][line[0]]['op'] + address
                        list_of_bin.append(bin_line)
                else:
                        print("Erro de sintaxe na linha {}.", pc)
        code = '\n'.join(list_of_bin)
        return code

def converterCodigoParaHexa(code):
        code = code.splitlines()
        codigo_hexadecimal = []
        for line in code:
                line = hex(int(line, 2))[2:].zfill(8)
                codigo_hexadecimal.append(line)
        codeHexa = ''.join(codigo_hexadecimal)
        return codeHexa
                         
def gerarArquivoTxt(text, name):
        output = open(name, 'w')
        output.write(text)

def gerarArquivoMif(code, name):
        ouput = open(name, 'w')
        ouput.write('WITH = 8;\nDEPTH = 512;\n\nADDRESS_RADIX = HEX;\nDATA_RADIX = HEX;\n\nCONTENT BEGIN\n')
        for i in range(0, len(code), 2):
                ouput.write('\t{} : {};\n'.format(hex(i)[2:].zfill(3), code[i]+code[i+1]))              
        ouput.write('END;')

#recebe o nome do arquivo a ser gerado no terminal
arquivosaida = sys.argv[2]

def Main():
        codigo = tratarCodigo(assemblyCode)
        codigo = removerLinhasBranco(codigo)
        labels = armazenarLabels(codigo)
        labels_positions = armazenarPosiçãoLabels(codigo)
        dicionario_labels = gerarDicionarioLabels(labels, labels_positions)
        codigo = removerLabels(codigo)
        lista_de_instrucoes = armazenarLinhasDeInstruções(codigo)
        codigo_binario = converterCodigoParaBinario(lista_de_instrucoes, dicionario_labels)
        gerarArquivoTxt(codigo_binario, 'CodigoBinario.txt') #apenas para analisar a saida das linhas em binário
        codigoHexadecimal = converterCodigoParaHexa(codigo_binario)
        gerarArquivoMif(codigoHexadecimal, arquivosaida)
Main()