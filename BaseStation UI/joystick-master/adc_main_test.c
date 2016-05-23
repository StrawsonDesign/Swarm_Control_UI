#include <stdio.h>
#include "adc.h"
#include <stdlib.h>
#include <unistd.h>

void main(){
	
	Joystick J;
	
	initialize_joystick(&J);
	
	printf("ch_0: %f\t%f\t%f\n",J.min[0],J.mid[0],J.max[0]);
	fflush(stdin);
	getchar();
	fflush(stdin);
	printf("ch_1: %f\t%f\t%f\n",J.min[1],J.mid[1],J.max[1]);
	fflush(stdin);
	getchar();
	fflush(stdin);
	printf("ch_2: %f\t%f\t%f\n",J.min[2],J.mid[2],J.max[2]);
	fflush(stdin);
	getchar();
	fflush(stdin);
	printf("ch_3: %f\t%f\t%f\n",J.min[3],J.mid[3],J.max[3]);
	fflush(stdin);
	getchar();
	fflush(stdin);
	while(1){
		
		
		get_all_values(&J);

		print_all_values(&J);
		
		usleep(30000);
	}
	
}
