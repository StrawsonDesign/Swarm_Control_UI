#ifndef ADC_H_
#define ADC_H_

typedef struct Joystick{
	float value[4];
	float min[4];
	float mid[4];
	float max[4];
	
}Joystick;

int get_adc_value(int ch);

int get_all_values(Joystick *J);

int initialize_joystick(Joystick *J);

int print_all_values(Joystick *J);

#endif
