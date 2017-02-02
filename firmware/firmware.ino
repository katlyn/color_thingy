#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

const bool flipped=true;
const int grid_width=8;
const int grid_height=8;
const int num_line_0=8;

Adafruit_NeoPixel pixels0(grid_width,A0,NEO_GRB+NEO_KHZ800);
Adafruit_NeoPixel pixels1(grid_width*(grid_height-1),A1,NEO_GRBW+NEO_KHZ800);

char crc(char* data,int size)
{
    char value=0x00;
    for(int ii=0;ii<size;++ii)
        value^=data[ii];
    return value;
}

void init_colors()
{
    pixels0.begin();
    pixels1.begin();
    for(unsigned int ii=0;ii<grid_width*grid_height;++ii)
            set_color(ii,50,0,0);
    update_colors();
}

void set_color(unsigned int ind,unsigned int rr,unsigned int gg,unsigned int bb)
{
    if(flipped)
        ind=grid_width*grid_height-ind-1;

    int new_ind=ind;

    if(new_ind>=num_line_0)
        new_ind-=num_line_0;

    int yy=new_ind/grid_width;
    int xx=new_ind%grid_width;

    if(yy%2!=0)
        xx=grid_width-xx-1;

    new_ind=yy*grid_width+xx;
    
    if(ind<num_line_0)
        pixels0.setPixelColor(new_ind,pixels0.Color(rr,gg,bb));
    else
        pixels1.setPixelColor(new_ind,pixels1.Color(rr,gg,bb,0));
}

void update_colors()
{
    pixels0.show();
    pixels1.show();
}

void setup()
{
    init_colors();
    Serial.begin(115200);
}

enum state_t
{
    HEADER_1,
    HEADER_2,
    DATA,
    CRC
};

state_t state=HEADER_1;
const int data_size=grid_height*grid_width*3;
char data_buf[data_size];
int data_ptr=0;

void loop()
{
    char temp;
    while(Serial.available()&&Serial.readBytes(&temp,1)==1)
    {
        if(state==HEADER_1&&temp=='a')
        {
            state=HEADER_2;
        }
        else if(state==HEADER_2&&temp=='z')
        {
            state=DATA;
            data_ptr=0;
        }
        else if(state==DATA)
        {
            data_buf[data_ptr++]=temp;
            if(data_ptr>=data_size)
                state=CRC;
        }
        else if(state==CRC)
        {
            if(crc(data_buf,data_size)==temp)
            {
                for(unsigned int ii=0;ii<grid_width*grid_height;++ii)
                        set_color(ii,
                            data_buf[ii*3+0],
                            data_buf[ii*3+1],
                            data_buf[ii*3+2]);
                update_colors();
            }
            state=HEADER_1;
        }
        else
        {
            state=HEADER_1;
        }
    }
}
