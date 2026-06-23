
//Automated Weapon Station

/*
Servo Module: This is the top module for the Servo.sv file. This module
tests the physical servo. It sweeps the PWM signal back and forth between 
500us - 2500us.
*/

//Gabriel Iniguez

module servo_test (
    input CLOCK0_50, //50MHz Clock from DE-25 board.
    input [3:0] KEY, //KEY[0] will be used as the Reset.
    output logic [35:0] GPIO_D //3.3V signal to level shifter.
);

    //Internal Signals
    logic [15:0] pwm_val; // The current target to send to the servo.
    logic [17:0] delay_counter; // Counter for the sweep (Optimized for 3ms).
    logic dir; // Direction: 1 = Sweeping Left, 0 = Sweeping Right.

    // Timing Constants
    // We will update the position every 3 milliseconds to perfectly match the digital servo.
    // 3ms * 50,000,000 Hz = 150,000 clock cycles.
    localparam int DELAY_MAX = 150_000;
    
    // Sweep Limits
    localparam logic [15:0] PWM_MIN = 16'd500;
    localparam logic [15:0] PWM_MAX = 16'd2500;
    localparam logic [15:0] PWM_STEP = 16'd5; // Move by 5 microseconds every 10ms.

    //Instantiate Servo.sv module
    Servo myServo (
        .clk(CLOCK0_50),
        .rst_n(KEY[0]),
        .pwm(pwm_val),
        .pwm_out(GPIO_D[0])
    );
    
    assign GPIO_D[35:1] = 35'd0; //Grounds the 35 pins left.
	 

    //The dummy python script for testing purposes.
     always_ff @(posedge CLOCK0_50) begin
        if (!KEY[0]) begin
            delay_counter <= 18'd0;
            pwm_val       <= 16'd1500; // Start at center (1.5ms)
            dir           <= 1'b1;     // Start by sweeping UP
        end else begin
            // If 3ms has passed, time to update the position
            if (delay_counter >= DELAY_MAX - 1) begin
                delay_counter <= 18'd0; // Reset the 3ms timer

                // Sweep Logic
                if (dir == 1'b1) begin // If we are going Left
                    if (pwm_val >= PWM_MAX) begin
                        dir <= 1'b0; // Reached the max, turn around
                        pwm_val <= pwm_val - PWM_STEP;
                    end else begin
                        pwm_val <= pwm_val + PWM_STEP; // Keep going up
                    end
                end else begin         // If we are going Right
                    if (pwm_val <= PWM_MIN) begin
                        dir <= 1'b1; // Reached the min, turn around
                        pwm_val <= pwm_val + PWM_STEP;
                    end else begin
                        pwm_val <= pwm_val - PWM_STEP; // Keep going down
                    end
                end
            end else begin
                // If 3ms hasn't passed, just keep ticking the timer
                delay_counter <= delay_counter + 18'd1;
            end
        end
    end

endmodule

