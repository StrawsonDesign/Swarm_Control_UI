#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <stdint.h>
#include <errno.h>
#include <unistd.h>
#include "adc.h"

int get_adc_value(int ch)
{
  int file;								
  int addr = 0x48;
  char *filename = "/dev/i2c-1";		// i2c bus 3 for XU4... 1 for BBB
  char buffer[2] = {0};					// buffer for incoming data
  int value;							// ADC value after decode
  value = 0;
  
  if ((file = open(filename, O_RDWR)) < 0) {
      perror("Opening i2c device node.\n");
      exit(1);
    }
    
  if (ioctl(file, I2C_SLAVE, addr) < 0) {
      perror("Failed to aquire bus access and/or talk to slave. \n");
      exit(1);
  }
  
  // choose MSB according to what channel to read.  Used in setup.
  char MSB[4] = {
    0b01000010,       // ch 0
    0b01010010,       // ch 1
    0b01100010,       // ch 2
    0b01110010};      // ch 3
  
  char setup[3] = {
    0b00000001,       // config address
    MSB[ch],          // MSB config bits
    0b10000011};      // LSB config bits
	
	// bit 15 		single shot conversion start	:no effect
	// bit 14-12	input multiplexer				:see above
	// bit 11-9		full scale configuration		:2.048V  001 4.096V
	// bit 8		single shot mode				:off
	// bit 7-5		data rate						:1600 SPS
	// bit 4		comparator mode					:traditional w/ hysteresis
	// bit 3		comparator polarity				:active low
	// bit 2		latching comparator				:off
	// bit 1-0		comparator queue and disable	:disable
	
   
  char setread[1] = {
    0b00000000};       // output register
   
	// write 3 bytes to ADC for set up including ch.
	// First byte, address and low write bit implied by write command.
  if (write(file, setup, 3) != 3) {
    perror("Error writing setup. \n");
    exit(1);
  }

  	// write 1 byte to ADC pointing to conversion register.
	// First byte, address and low write bit implied by write command.
  if (write(file, setread, 1) != 1) {
    perror("Error writing setread. \n");
    exit(1);
  }
  
  usleep(1000); 	// wait for ADC sample to finish. 1/1600 sec + ~400us
  
    // Read from Conversion register.
	// First byte, address and high read bit implied by read command.
  if (read(file, buffer, 2) != 2) {
    perror("Error reading to buffer");
    exit(1);
  }

  close(file);
   // Shift bits in buffer to correct position.
  value = ((buffer[0] << 8) | buffer[1]) >> 4;
  
  return(value);
}


int get_all_values(Joystick *J){

	int raw[4] = {0};
	int deadzone = 5;
	int i;
	raw[0] = get_adc_value(0);
	raw[1] = get_adc_value(1);
	raw[2] = get_adc_value(2);
	raw[3] = get_adc_value(3);
	
	for(i=0;i<4;i++){
		if (raw[i] > (J->mid[i] + deadzone)){
			J->value[i] = (raw[i] - (J->mid[i] + deadzone))/(J->max[i] - (J->mid[i] + deadzone));
				if (J->value[i] > 1.0) J->value[i] = 1.0;
		}
		else if (raw[i] < (J->mid[i] - deadzone)){
			J->value[i] = (raw[i] - (J->mid[i] - deadzone))/((J->mid[i] - deadzone) - J->min[i]);	
				if (J->value[i] < -1.0) J->value[i] = -1.0;
		}
		else {
			J->value[i] = 0.0;
		}
	}
	
	return 1;
}


int print_all_values(Joystick *J){
	printf("LH: %f\tLV: %f\tRH: %f\tRV: %f\n",
	J->value[2],J->value[3],J->value[0],J->value[1]);
	
	return 1;
}

int initialize_joystick(Joystick *J){


	////
	printf("Hold right joystick all the way right.\n");
	printf("Press ENTER when ready.\n");
	fflush(stdin);
	getchar();
	fflush(stdin);
	J->min[0] = get_adc_value(0);
	
	printf("Hold right joystick all the way left.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->max[0] = get_adc_value(0);

	printf("Hold right joystick all the way down.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->min[1] = get_adc_value(1);
	
	printf("Hold right joystick all the way up.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->max[1] = get_adc_value(1);

	////
	
	printf("Hold left joystick all the way right.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->min[2] = get_adc_value(2);
	
	printf("Hold left joystick all the way left.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->max[2] = get_adc_value(2);

	printf("Hold left joystick all the way down.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->min[3] = get_adc_value(3);
	
	printf("Hold left joystick all the way up.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->max[3] = get_adc_value(3);

	printf("Let go of both joysticks.\n");
	printf("Press ENTER when ready.\n");
	getchar();
	fflush(stdin);
	J->mid[0] = get_adc_value(0);
	J->mid[1] = get_adc_value(1);	
	J->mid[2] = get_adc_value(2);	
	J->mid[3] = get_adc_value(3);	

	printf("Initialization complete.\n");
	return 1;
	
}
