
//Automated Weapon Station

/*
Servo Module: This module controls the 35kg 300Hz panning digital servo
of the AWS. It consists of a 16-bit PWM signal that drives the servo,
an 18 bit internal signal (counter) that tracks the 150,000 clock cycles
for a 3ms pulse, and an 18-bit internal signal (pulseHigh) that tracks
how long the HIGH of the PWM singal lasts.
*/

//Gabriel Iniguez

module Servo (
    input clk, rst_n, //50MHz Clock from DE-25.
    input [15:0] pwm, //PWM signal is 16-bits so we can fit 500-2500 from python script.
    output pwm_out //Output signal (3.3v) to level shifter for 5.5v to servo (1-bit, Serial communication).
);


/*
Counter: 18-bit counter to hold 1,000,000 clock ticks. The servo expects a 3ms
control pulse (1/300Hz) so we need a way for the FPGA to keep track of time to send
the complete 3ms pulse to the servo. The clock is 50MHz (50,000,000/s) and the time
we need to track is 3ms (0.003s). So (50,000,000/s) * (0.003s) = 150,000 Clock cycles
for 3ms. Every 150,000 clock cycles is 3ms. This is how the FPGA will track time.
*/

/*
pulseHigh: We are measuring the length of the HIGH pulse (PWM). The FPGA
multiplies the data from the pyton script by 50 (50MHz clk) to obtain the 
length of the HIGH pulse in clock cycles. (1500 * 50 = 75,000clk cycles)
75,000 clk cycles = 1500 micro seconds. This length is sent to the servo
which then does the correct action based on the length of the HIGH pulse. 
*/
logic [17:0] counter; //0 - 149,999 clk cycles for 3ms pulse.
logic [17:0] pulseHigh; //The amount of clock cycles a HIGH lasts (Length of HIGH pulse). (1500 * 50 = 75,000clk cycles).


//Multiplier that converterts the microseconds from the python script to clock cycles for the FPGA. (Finish line)
assign pulseHigh = pwm * 18'd50;

//Sequential logic: Keeps track of the 20ms control pulse.
always_ff @(posedge clk) begin
    //If reset is pressed, zero out.
    if(!rst_n) begin
        counter <= 18'd0;
    end else begin
        //If we hit  or more we go back to zero.
        if(counter >= 18'd149_999) begin
            counter <= 18'd0;
        end else begin
        //Otherwise, keeping ticking by 1
        counter <= counter + 18'd1;
        end
    end
end

/*
If the counter is less than the pulseHigh then send the 3.3v.
We left the pwm_out signal out of the sequential logic so we do not
have to wait 1 clk cycle to send the signal.
*/
assign pwm_out = (pulseHigh > counter) ? 1'b1 : 1'b0;

endmodule


//Testbench

`timescale 1ns / 1ps

module servo_testbench();
    logic clk;
    logic rst_n;
    logic [15:0] pwm;
    logic pwm_out;

    //Array to hold the 10 test variables.
    localparam int testNums = 10; 
    logic [15:0] testArray [0:testNums-1];//Allocates memory to store the 10 16-bit numbers.
    int i;
 
    //Instantiate to the main module.
    Servo DUT (
        .clk(clk),
        .rst_n(rst_n),
        .pwm(pwm),
        .pwm_out(pwm_out)
    );

    //Generate the 50MHz clock.
    always #10 clk = ~clk; //10 nanosecond toggle

    //Monitor block
    initial begin
        $display("    Time\t | Reset\t | PWM\t | PWM_Out");
        $display("--------------------------------------");
	$timeformat(-9, 0, "ns", 10);//Format the time to 10^{-9} (nanoseconds), show 0 decimal places, add the string 'ns' to the end, and give it 10 spaces of padding.
        $monitor(" %8t | %b\t |  %d\t |     %d", $time, rst_n, pwm, pwm_out);
    end

    //Stimulus Block
    initial begin

      //Load random numbers from 500-2500 into testArray.
      for(i = 0; i < testNums; i++) begin
	testArray[i] = $urandom_range(2500,500);
      end

      //Initialize the system.
      clk = 0;
      rst_n = 0;
      pwm = 16'd1500;
      #100;

      //Release the reset.
      rst_n = 1;

      //Loop through the 10 test cases.
      for(i = 0; i < testNums; i++) begin
	pwm = testArray[i];
	#3000000;//Wait 3ms for full PWM signal.
      end

        $stop;
    end
endmodule





            


