from PIL import Image

fil = "testcard"

acc = [0,0,0,255]
buffer = [[0,0,0,0] for _ in range(64)]

def losslessRead(file):
    a=open(file, 'rb')
    b=a.read()
    a.close()
    return b

def getbits(num):
    return [1 if num & (1 << (7-n)) else 0 for n in range(8)]

def halfnum(num, half):
    return num>>4 if not half else num - (num>>4<<4)

def addbits(num):
    return num[0]*2+num[1]

def main():
    global acc
    global buffer

    a=losslessRead('test_images\\{fil}.qoi')
    i = 0
    j = 0
    finished = False
    if(a[:4]==b'qoif'):
        i+=4
        width = int.from_bytes(a[i:i+4],'big')
        i+=4
        height = int.from_bytes(a[i:i+4],'big')
        i+=4
        #channels = a[i]
        #tipus = a[i+1]
        i+=2
        d=Image.new("RGBA",(width,height))
        e=Image.open(fil+".png").convert('RGBA')
        while not finished:
            if(a[i]==0):
                end = True
                for k in range(7):
                    if(a[i+k]):
                        end = False
                if a[i+7]==1 and end:
                    finished = True
            if(a[i]==254): #set rgb
                c = [a[i+1],a[i+2],a[i+3],acc[3]]
                buffer[(c[0]*3+c[1]*5+c[2]*7+c[3]*11)%64] = c
                acc = c
                d.putpixel((j%width,j//width), (c[0],c[1],c[2],c[3]))
                i+=4
            elif(a[i]==255): #setrgba
                c = [a[i+1],a[i+2],a[i+3],a[i+4]]
                buffer[(c[0]*3+c[1]*5+c[2]*7+c[3]*11)%64] = c
                d.putpixel((j%width,j//width), (c[0],c[1],c[2],c[3]))
                acc = c
                i+=5
            elif(a[i]<64): #set from buffer
                c = buffer[a[i]]
                acc = c
                d.putpixel((j%width,j//width), (c[0],c[1],c[2],c[3]))
                i+=1
            elif(a[i]<128): #acc + dx (petit)
                c = [(acc[0]+addbits(getbits(a[i])[2:4])-2)%256,(acc[1]+addbits(getbits(a[i])[4:6])-2)%256,(acc[2]+addbits(getbits(a[i])[6:])-2)%256,acc[3]]
                buffer[(c[0]*3+c[1]*5+c[2]*7+c[3]*11)%64] = c
                d.putpixel((j%width,j//width), (c[0],c[1],c[2],c[3]))
                acc = c
                i+=1
            elif(a[i]<192): #acc + dx (gran)
                c=acc
                dg = a[i]-128-32
                dr = halfnum(a[i+1],0) + dg - 8
                db = halfnum(a[i+1],1) + dg - 8
                c = [(acc[0]+dr)%256,(acc[1]+dg)%256,(acc[2]+db)%256,acc[3]]
                buffer[(c[0]*3+c[1]*5+c[2]*7+c[3]*11)%64] = c
                d.putpixel((j%width,j//width), (c[0],c[1],c[2],c[3]))
                acc = c
                i+=2
            elif(a[i]<254): #run
                r = a[i]-192
                c=acc
                for _ in range(r+1):
                    d.putpixel((j%width,j//width), (c[0],c[1],c[2],c[3]))
                    j+=1
                i+=1
                j-=1
            j+=1
            if j>=height*width:
                finished=True
    else:
        print('file is not originally a .qoi')
    d.show()
main()