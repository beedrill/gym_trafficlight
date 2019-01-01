import os
#node is defined as (j,i) where j is the j'th column from left to right and i is the i'th row from bottom up
def node_text(name,x,y,type):
        s="<node id=\"";
        s=s+str(name);
        s=s+'\" x=\"';
        s=s+str(x)+'\" y=\"'+str(y)+"\" type=\""+type+"\" />";
        #s='v';
        return s;

def node_set_text(col,row,dis):
        s="<nodes>\n";
        #counter=0;
        for i in range(1,row+1):
                for j in range(1,col+1):
                        #counter=counter+1;
                        if (i==1 and j==1) or (i==1 and j==col) or (i==row and j==1) or (i==row and j==col):
                                continue
                        if i==1 or j==1 or i==row or j==col:
                                s=s+node_text("("+str(j)+","+str(i)+")",(j-(col+1)/2)*dis,(i-(row+1)/2)*dis,"priority")+"\n";
                        else:
                                s=s+node_text("("+str(j)+","+str(i)+")",(j-(col+1)/2)*dis,(i-(row+1)/2)*dis,"traffic_light")+"\n";
        s=s+"</nodes>";
        return s;

def edge_text(name,fr,t,type):
        s="<edge id=\"";
        s=s+str(name);
        s=s+'\" from=\"';
        s=s+str(fr)+'\" to=\"'+str(t)+"\" type=\""+type+"\" />";
        return s;

def node_id(row,col):
        return "("+str(row)+","+str(col)+")";
        
def edge_set_text(col,row,typ):
        s="<edges>\n";
        #counter=0;
        for i in range(1,row+1):
                for j in range(1,col+1):
                        
                        ##if i!=row:
                         #       #counter=counter+1;
                          ##      s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j)+"_"+str(i+1),node_id(j,i),node_id(j,i+1),"d")+"\n";
                                
                                #counter=counter+1;
                                #s=s+edge_text("e"+str(counter),node_id(j,i+1),node_id(j,i),"d")+"\n";
                           ##     s=s+edge_text("e_"+str(j)+"_"+str(i+1)+"_"+str(j)+"_"+str(i),node_id(j,i+1),node_id(j,i),"d")+"\n";
                                
                                
                        ##if j!=col:
                                #counter=counter+1;
                                #s=s+edge_text("e"+str(counter),node_id(j,i),node_id(j+1,i),"d")+"\n";
                         ##       s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j+1)+"_"+str(i),node_id(j,i),node_id(j+1,i),"d")+"\n";
                                #counter=counter+1;
                                #s=s+edge_text("e"+str(counter),node_id(j+1,i),node_id(j,i),"d")+"\n";
                          ##      s=s+edge_text("e_"+str(j+1)+"_"+str(i)+"_"+str(j)+"_"+str(i),node_id(j+1,i),node_id(j,i),"d")+"\n";
                        if (i==1 and j==1) or (i==1 and j==col) or (i==row and j==1) or (i==row and j==col):
                                continue
                        if i==1:
                                s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j)+"_"+str(i+1),node_id(j,i),node_id(j,i+1),typ)+"\n";
                                continue
                        if i==row:
                                s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j)+"_"+str(i-1),node_id(j,i),node_id(j,i-1),typ)+"\n";
                                continue
                        if j==1:
                                s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j+1)+"_"+str(i),node_id(j,i),node_id(j+1,i),typ)+"\n";
                                continue
                        if j==col:
                                s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j-1)+"_"+str(i),node_id(j,i),node_id(j-1,i),typ)+"\n";
                                continue
                        s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j)+"_"+str(i+1),node_id(j,i),node_id(j,i+1),typ)+"\n";
                        s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j+1)+"_"+str(i),node_id(j,i),node_id(j+1,i),typ)+"\n";
                        s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j)+"_"+str(i-1),node_id(j,i),node_id(j,i-1),typ)+"\n";
                        s=s+edge_text("e_"+str(j)+"_"+str(i)+"_"+str(j-1)+"_"+str(i),node_id(j,i),node_id(j-1,i),typ)+"\n";
        
                               
        s=s+"</edges>";
        return s;
        

def generateMap(col,row,name,edge_length = 125,lane_type='d'):
        print "generate map for %s" % name
        node_file=open(name+'.nod.xml','w');
        node_file.write(node_set_text(col,row,edge_length))
        node_file.close();
#print(edge_text("1_2",1,2,"b"));
#print(edge_set_text(3,4));
        edge_file=open(name+'.edg.xml','w');
        edge_file.write(edge_set_text(col,row,lane_type));
        edge_file.close();
        os.system("netconvert --node-files=%s.nod.xml --type-files=%s.typ.xml --edge-files=%s.edg.xml --output-file=%s.net.xml" %(name,name,name,name))

if __name__ == "__main__":
    generateMap(4,3,'traffic');
