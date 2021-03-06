#!/usr/bin/python
import vcf
import argparse


def snp_index(sample):
    num=sum([record.genotype(x)[field] for x in sample])
    den=sum([record.genotype(x)["DP"] for x in sample])
    return float(num)/den

def snp_index_ls(sample,index):
    num=sum([record.genotype(x)[field][index] for x in sample])
    den=sum([record.genotype(x)["DP"] for x in sample])
    return float(num)/den

def get_bfr(index1,index2):
    if index2==0:
        return float('inf')
    else:
        return index1/index2

def print_row():
    global total
    bfr=get_bfr(snpinxA,snpinxB)
    if record.ID==None:
        fid='.'
    else:
        fid=str(record.ID)
    print str(record.CHROM)+'\t'+str(record.POS)+'\t'+fid+'\t'+str(record.REF)+'\t'+ALT+'\t'+str(snpinxA)+'\t'+str(snpinxB)+'\t'+str(bfr)+'\t'+str(dpa)+'\t'+str(dpb)
    total+=1


parser = argparse.ArgumentParser(description="Calculate BFR")
parser.add_argument('vcf',type=str,help="vcf file")
#parser.add_argument('-s1','--sample1',type=str,help="sample 1",required=True)
#parser.add_argument('-s2','--sample2',type=str,help="sample 2",required=True)
parser.add_argument('--mindp',type=int,default=0,help="DP minimum treshold")
parser.add_argument('-t','--trait',type=str,nargs='+',required=True,help="trait samples")
parser.add_argument('-b','--base',type=str,nargs='+',required=True,help="base samples")
parser.add_argument('--field',type=str,default="AO",help="SNP index numerator/ default=AO")
parser.add_argument('-f','--filter',type=str,nargs='+',help="filter for different GT")
args = parser.parse_args()
filt=args.filter
if filt:
    if len(filt)<2:
        print "--filter requires at least two samples"
        quit()
a=args.vcf
#samone=args.sample1
#samtwo=args.sample2
base=args.base
trait=args.trait
mindp=args.mindp
field=args.field

total=0
nocov=0
averone=0.0
avertwo=0.0
records=0
nofilt=0
vcf_reader=vcf.Reader(open(a,'r'))
print "#CHROM"+'\t'+"POS"+'\t'+"ID"+'\t'+"REF"+'\t'+"ALT"+'\t'+"SI_trait"+'\t'+"SI_base"+'\t'+"BFR"+'\t'+"DP_trait"+'\t'+"DP_base"
for record in vcf_reader:
    records+=1
    dpa=sum([record.genotype(x)["DP"] for x in trait])
    dpb=sum([record.genotype(x)["DP"] for x in base])
    averone+=dpa
    avertwo+=dpb
    if filt:
        if all(record.genotype(x)["GT"]==record.genotype(filt[0])["GT"] for x in filt[1:]):
            nofilt+=1
            continue
    if dpa>mindp and dpb>mindp:
        if len(record.ALT)>1:
            for index,variant in enumerate(record.ALT):
                snpinxA=snp_index_ls(trait,index)
                snpinxB=snp_index_ls(base,index)
                ALT=str(variant)
                print_row()
        else:
            snpinxA=snp_index(trait)
            snpinxB=snp_index(base)
            ALT=str(record.ALT).strip('[]')
            print_row()
    else:
        nocov+=1
##### creating stats file
stats_file=open(a[:-4]+"_stats.txt",'w')
print >>stats_file, "Samples used:", trait, base
print >>stats_file, "SNPs and variants called:", total
print >>stats_file, "SNPs and variants discarded for low coverage:", nocov
print >>stats_file, "SNPs and variants discarded for GT filter:", nofilt
print >>stats_file, "Average coverage samples", trait,":", averone/records
print >>stats_file, "Average coverage sample", base,":", avertwo/records
stats_file.close()
