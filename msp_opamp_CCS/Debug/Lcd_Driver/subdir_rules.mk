################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Each subdirectory must supply rules for building sources it contributes
Lcd_Driver/%.obj: ../Lcd_Driver/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'MSP430 Compiler: "$<"'
	"C:/ti/ccs2051/ccs/tools/compiler/ti-cgt-msp430_21.6.1.LTS/bin/cl430" -vmsp -O3 --use_hw_mpy=none --include_path="C:/ti/ccs2051/ccs/ccs_base/msp430/include" --include_path="C:/Users/herhe/workspace_ccstheia/msp_opamp" --include_path="C:/Users/herhe/workspace_ccstheia/msp_opamp/GrLib/grlib" --include_path="C:/Users/herhe/workspace_ccstheia/msp_opamp/GrLib/fonts" --include_path="C:/ti/ccs2051/ccs/tools/compiler/ti-cgt-msp430_21.6.1.LTS/include" --advice:power="none" --define=__MSP430G2553__ -g --gcc --printf_support=minimal --diag_warning=225 --diag_wrap=off --display_error_number --preproc_with_compile --preproc_dependency="Lcd_Driver/$(basename $(<F)).d_raw" --obj_directory="Lcd_Driver" $(GEN_OPTS__FLAG) "$<"


