
#!/bin/bash
gbtiler --argfile copper.txt 
gbtiler --argfile silk.txt 
gbtiler --argfile solder.txt 
gbtiler --argfile drill.txt
rm workspace/*.MERGED
gerbv -x png -o stichedBC.png workspace/copperStiched.GBL 
gerbv -x png -o stichedTC.png workspace/copperStiched.GTL
gerbv -x png -o stichedDR.png workspace/drillStiched.DRL
gerbv -x png -o stichedSST.png workspace/silkStiched.GTO
gerbv -x png -o stichedSB.png workspace/solderStiched.GBS
gerbv -x png -o stichedST.png workspace/solderStiched.GTS