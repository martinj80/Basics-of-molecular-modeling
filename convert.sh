#FROM TXT:
#obabel -ismi ZINC15_fda_corr.smi -O ZINC15_fda_Ro5_2D.sdf --gen2d -e --filter 'MW<=500 logP<=5 HBD<=5 HBA2<=10 abonds>1 rotors<10 (s="[!H0;F,Cl,Br,I,N+,$([OH]-*=[!#6]),+]" || s="[$([C,S](=[O,S,P])-[O;H1,-1])]" || s="[$([#16X4]([N!H0])(=[OX1])(=[OX1])[#6]),$([#16X4+2]([N!H0])([OX1-])([OX1-])[#6])]")'
#obabel -isdf ZINC15_fda_2D.sdf -O ZINC15_fda_Ro5_3D.sdf --gen3d -e -p 7.4 --unique inchi 

#FROM SDF: Needs openbabel version 3.1.0
#https://www.daylight.com/dayhtml_tutorials/languages/smarts/smarts_examples.html
#https://www.rdkit.org/docs/GettingStartedInPython.html

#protonation and gen2d does not work in one step from SMILES
#1.add explicit hydrogens based on pH
obabel -ismi *.smi -O ZINC15_fda_p7.4.sdf -p 7.4
#2.generate 2D coordinates
obabel -isdf ZINC15_fda_p7.4.sdf -O ZINC15_fda_p7.4_2D.sdf --gen2d
#2.generate 3D coordinates
obabel -isdf ZINC15_fda_p7.4_2D.sdf -O ZINC15_fda_p7.4_3D.sdf --gen3d



obabel -isdf ZINC15_fda.sdf -O ZINC15_fda_Ro5_7.4.sdf -p 7.4 --addoutindex --unique inchi --filter 'MW<=500 logP<=5 HBD<=5 HBA2<=10 abonds>1 rotors<10 (s="[!H0;F,Cl,Br,I,N+,$([OH]-*=[!#6]),+]" || s="[$([C,S](=[O,S,P])-[O;H1,-1])]"'

mk_prepare_ligand.py -i ZINC15_fda_Ro5_7.4.sdf --multimol_outdir Ligands
