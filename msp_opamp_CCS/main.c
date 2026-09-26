#include <msp430.h>

// Variables globales para el ADC
volatile unsigned int adc_raw_value = 0;
volatile float v_adc = 0.0;
volatile float v_bateria = 0.0;

// Configuración del ADC10
void init_ADC(void) {
    ADC10AE0 |= BIT0;                          // Habilita entrada analógica en P1.0 (A0)
    ADC10CTL0 = SREF_1 + ADC10SHT_2 + ADC10ON; // Ref interna 2.5V, 16 ciclos muestreo, ADC ON
    ADC10CTL0 |= REF2_5V + REFON;              // Selecciona 2.5V y enciende referencia
    ADC10CTL1 = INCH_0;                        // Canal A0
    __delay_cycles(1000);                      // Espera a que la referencia se estabilice
}

// Función de envío de texto por UART 
void ser_output(char *str) {
    while(*str != 0) {
        while (!(IFG2 & UCA0TXIFG));
        UCA0TXBUF = *str++;
    }
}

// Convierte un float simple a texto en un buffer (sin usar sprintf)
void float_to_string(float val, char *buffer) {
    int entero = (int)val;
    int decimales = (int)((val - entero) * 100);
    if (decimales < 0) decimales = -decimales;

    // Encabezado
    buffer[0] = 'V'; buffer[1] = 'o'; buffer[2] = 'l'; buffer[3] = 't'; 
    buffer[4] = 'a'; buffer[5] = 'j'; buffer[6] = 'e'; buffer[7] = ':'; 
    buffer[8] = ' ';

    // Parte entera
    buffer[9] = '0' + (entero % 10);
    buffer[10] = '.';

    // Parte decimal (dos dígitos)
    buffer[11] = '0' + (decimales / 10);
    buffer[12] = '0' + (decimales % 10);

    // Final de línea
    buffer[13] = ' '; buffer[14] = 'V'; 
    buffer[15] = '\r'; buffer[16] = '\n'; 
    buffer[17] = '\0';
}

void main(void) {
    WDTCTL = WDTPW | WDTHOLD;

    // Calibración del reloj a 1MHz
    BCSCTL1 = CALBC1_1MHZ;
    DCOCTL = CALDCO_1MHZ;

    // Configuración UART a 19200 baudios
    P1SEL = BIT1 | BIT2;
    P1SEL2 = BIT1 | BIT2;
    
    UCA0CTL1 |= UCSWRST + UCSSEL_2;
    UCA0BR0 = 52;  // Settings para 19200 baudios a 1MHz
    UCA0BR1 = 0;
    UCA0MCTL = UCBRS_0;
    UCA0CTL1 &= ~UCSWRST;

    init_ADC();

    char buffer_texto[20];

    while(1) {
        // 1. Muestreo del ADC
        ADC10CTL0 |= ENC + ADC10SC;
        while (ADC10CTL0 & ADC10BUSY);
        adc_raw_value = ADC10MEM;

        // 2. Cálculos de voltaje
        v_adc = (adc_raw_value * 2.5) / 1023.0;
        v_bateria = v_adc / 0.51546;

        // 3. Convertir voltaje a cadena de texto y enviar
        float_to_string(v_bateria, buffer_texto);
        ser_output(buffer_texto);

        // 4. Pausa de medio segundo entre lecturas
        __delay_cycles(500000);
    }
}
