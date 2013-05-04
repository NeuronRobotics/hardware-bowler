#!/usr/bin/env python

import os,sys,pygame,time
from pygame.locals import *

class gerber():
    path=""
    image=None
    dimentions=(0,0)
    position=(0,0)
    surface=None
    rect=None
    scaler = 1.35
    toInches = 1.35/100
    def __init__(self,Path,window):
        self.path=Path
        self.WindowSize=window
        out = "gerbv -x png -o "+self.path+"/out.png "+self.path+"/bottom_copper.GBL "+self.path+"/top_copper.GTL "+self.path+"/top_silk.GTO "
        os.system(out)
        self.image=pygame.image.load(self.path+"/out.png")
        self.dimentions=self.image.get_size()
        self.surface = pygame.Surface(self.dimentions).convert()
        self.rect = self.surface.get_rect()
        try:
            f = open(self.path+"/position.txt",'r')
            pos = f.read()
            f.close
            print "Position File Contents:",pos
            pos_split= pos.split(',')
            self.position=(float(pos_split[0]),float(pos_split[1]))
            self.rect = self.rect.move(self.position)
        except:
            print "no position file"
        print out,self.dimentions,self.getAreaInches()
    def getAreaInches(self):
        return self.dimentions[0]*self.dimentions[1]*self.toInches*self.toInches
    def save(self):
        pos = str(self.rect.topleft[0])+','+str(self.rect.topleft[1])
        print "Saving Position to file",pos
        f = open(self.path+"/position.txt",'w')
        f.write(pos)
        f.close
    def strX(self):
        return str(float(self.rect.bottomleft[0])*self.toInches)
    def strY(self):
        return str(float( (self.WindowSize[1]- self.rect.bottomleft[1]))*self.toInches)
class motion():
    MovingImage=False
    gerberIndex=0
    originX=0
    originY=0
    def __init__(self):
        pass
def export(gerbers):
    print "Starting Export"
    header = """
--leading_zeroes 0
--trailing_zeroes 0
--x_integer_digits 2
--x_decimal_digits 4
--y_integer_digits 2
--y_decimal_digits 4
"""
    gerbfile = "\n   --gerberfile "
    drillfile = "\n   --drillfile"
    layer = "\n--layer "
    outfile =  "\n   --outfile "
    offset =   "\n      --offset "
    layers = ["top","bottom","drill"]
    copper = ["/bottom_copper.GBL","/top_copper.GTL"]
    silk =   ["/bottom_silk.GBO","/top_silk.GTO"]
    solder = ["/bottom_soldermask.GBS","/top_soldermask.GTS"]
    drill  = ["/drill.DRD"]
    
    run = """
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
gerbv -x png -o stichedST.png workspace/solderStiched.GTS"""
    def MakeOutFile(outFile,type,gerbers,layerLetter):
        
        back = header+layer+"bottom"
        for i in gerbers:
            back +=gerbfile + ' '+ i.path+type[0]
            back +=offset + i.strX()+' '+i.strY()
        back +=outfile+ outFile+'.GB'+layerLetter
        back +=layer+"top"
        for i in gerbers:
            back +=gerbfile + ' '+ i.path+type[1]
            back +=offset + i.strX()+' '+i.strY()
        back +=outfile+ outFile+'.GT'+layerLetter
        return back   
    
    #silkOut = MakeOutFile('silkStiched',silk,dirs,'O') 
    silkOut = header+layer+"top"
    for i in gerbers:
        silkOut +=gerbfile + ' '+ i.path+silk[1]
        silkOut +=offset + i.strX() +' '+i.strY()
    silkOut +=outfile+'silkStiched.GTO'
    
    copperOut = MakeOutFile('copperStiched',copper,gerbers,'L')
    solderOut = MakeOutFile('solderStiched',solder,gerbers,'S')
    
    drillOut = header+layer+"drill"
    for i in gerbers:
        drillOut +=drillfile + ' '+ i.path+drill[0]
        drillOut +=offset + i.strX()+' '+i.strY()
    drillOut +=outfile+'drillStiched.DRL'
    f = open('copper.txt','w')
    f.write(copperOut)
    f.close
    f = open('silk.txt','w')
    f.write(silkOut)
    f.close
    f = open('solder.txt','w')
    f.write(solderOut)
    f.close
    f = open('drill.txt','w')
    f.write(drillOut)
    f.close
    f = open('run.sh','w')
    f.write(run)
    f.close
    os.system(run)
    
def main():
    print "Starting"
    WindowSize = (900,900)
    window = pygame.display.set_mode(WindowSize)
    screen = pygame.display.get_surface()
    pygame.display.flip()
    pygame.display.set_caption('Gerber Sticher')   
    processButton = pygame.Surface((50,50)).convert()
    processButton.fill((255,255,255))
    pb = processButton.get_rect()
    pb.topright=(((900),0))
    
    list = os.listdir('.') 
    gerbers = []
    for i in list:
        if i.find('.')<0  and i.find('workspace')<0:
            new =''
            for j in i:
                if j is not' ' and j is not ')' and j is not '(':
                    new+=j
            os.system("mv \""+i+"\" "+new)
            gerbers.append(gerber(new,WindowSize))
    totalBoardArea = 0
    for i in gerbers:
          totalBoardArea +=i.getAreaInches()   
    print totalBoardArea
    area=0
    mover=motion()
    fX=0
    fY=0
    toInches = 1.35/100
    while 1:
        for event in pygame.event.get():
            if event.type==QUIT:
                print "Exiting"
                sys.exit(0)
            if event.type==MOUSEBUTTONDOWN:
                mover.originX = ep[0]
                mover.originY = ep[1]
                start=ep
                i=0
                while i < len(gerbers):
                    g = gerbers[i].rect
                    if g.collidepoint(start):
                        mover.gerberIndex = i
                        mover.MovingImage = True
                    i+=1
                if pb.collidepoint(start):
                    export(gerbers)
                    f = open('dimentions.txt','w')
                    out = "X="+str((float(fX)*toInches))+",Y="+str(float(WindowSize[1]-fY)*toInches)
                    print "Dimentions=",out
                    f.write(out )
                    f.close()
                    for i in gerbers:
                        i.save()
            if event.type==MOUSEBUTTONUP:
                ep = event.pos
                if mover.MovingImage:
                    mi = mover.gerberIndex
                    movePos = [(ep[0]-mover.originX),(ep[1]-mover.originY)]
                    #print movePos
                    gerbers[mi].rect = gerbers[mi].rect.move(movePos)
                    mover.MovingImage= False
                    fX = 0
                    fY = WindowSize[1]
                    for i in gerbers:
                        try:
                            pX = i.rect.topright[0]
                            pY = int(i.rect.topright[1])
                            if fX < pX:
                                fX = pX
                            if (fY > pY):
                                fY = pY
                        except:
                            print "off screen"
                    area = (float(fX)*toInches)*(float(WindowSize[1]-fY)*toInches)
            if event.type==MOUSEMOTION:
                ep = event.pos
                if mover.MovingImage:
                    mi = mover.gerberIndex
                    movePos = [(ep[0]-mover.originX),(ep[1]-mover.originY)]
                    gerbers[mi].rect = gerbers[mi].rect.move(movePos)
                    mover.originX = ep[0]
                    mover.originY = ep[1]
        if area < 60:
            screen.fill((0,255,0)) 
        else:
            screen.fill((255,0,0)) 
        pygame.display.set_caption('Gerber Sticher '+str(area)+" in^2 of "+str(totalBoardArea))
        for i in gerbers:
            screen.blit(i.image,i.rect)
        screen.blit(processButton,pb)
        pygame.draw.circle(screen, (0,0,255), (fX,fY), 2, 0)
        pygame.display.update()
        time.sleep(.1)
        
if __name__ == "__main__":
    main()
