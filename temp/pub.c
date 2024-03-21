#include <stdlib.h>
#include <stdio.h>

int main() {
    // Command to execute
    const char *command = "mosquitto_pub -u internal -P mqttcci -t subs/change -m 1";

    // Execute the command
    int result = system(command);

    // Check the result
    if (result == -1) {
        // Failed to execute the command
        perror("Error executing the command");
        return 1;
    } else if (result != 0) {
        // Command returned an error
        printf("Command returned non-zero exit code: %d\n", result);
        return 1;
    }

    // Command executed successfully
    printf("Command executed successfully\n");
    return 0;
}
