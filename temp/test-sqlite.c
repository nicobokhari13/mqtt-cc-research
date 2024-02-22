#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <string.h>
#include "cJSON.h"

// Callback function for SELECT queries
// argc is the number of columns
// argv holds the values for each colum
static int callback(void *data, int argc, char **argv, char **columns) {
    int i;
    for (i = 0; i < argc; i++) {
        printf("%s = %s\t", columns[i], argv[i] ? argv[i] : "NULL");
    }
    printf("\n");
    return 0;
}

static int getJSONvalue(void *data, int argc, char **argv, char **columns){
    printf("In getJSONvalue \n");
    int i;
    for(i = 0; i < argc; i++){
        printf("In for loop \n");
        if(strcmp(columns[i], "name") == 0){
            printf("column: %s, value: %s", columns[i], argv[i]);
            break;
        }
    }
    cJSON *json = cJSON_Parse(argv[i]);
    printf("outside for loop \n");
    if (json == NULL) { 
        const char *error_ptr = cJSON_GetErrorPtr(); 
        if (error_ptr != NULL) { 
            printf("Error: %s\n", error_ptr); 
        } 
        cJSON_Delete(json); 
        return 1; 
    } 
    cJSON *clientID = cJSON_GetObjectItemCaseSensitive(json, "sub01");
    printf("got sub01 \n");
    const char * result = cJSON_Print(clientID);
    printf("cJSON clientID sub01, value: %s \n", result);
    if(cJSON_IsString(clientID)){
        printf("ClientID: sub01, Latency: %s \n", clientID->valuestring);
    }
    return 0;
}


char* createLatStr(){
    cJSON *jsonExample = cJSON_CreateObject();
    cJSON_AddNumberToObject(jsonExample, "sub01", 100);
    cJSON_AddNumberToObject(jsonExample, "sub02", 95);
    cJSON_AddNumberToObject(jsonExample, "sub02", 80);
    return cJSON_Print(jsonExample);
}

const char *concat_strings(const char *str1, const char *str2) {
    // Allocate memory for the concatenated string
    size_t len1 = strlen(str1);
    size_t len2 = strlen(str2);
    char *result = malloc(len1 + len2 + 1); // +1 for the null terminator
    if (result == NULL) {
        perror("Memory allocation failed");
        return NULL;
    }

    // Copy str1 and str2 into the result buffer
    strcpy(result, str1);
    strcat(result, str2);

    return result;
}

int main() {
    
    const char *json_str = createLatStr();
    sqlite3 *db;
    char *err_msg = 0;

    // Open the database (creates a new one if it doesn't exist)
    int rc = sqlite3_open("example.db", &db);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        return rc;
    }

    // Create a table
    const char *create_table_sql = "CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, name TEXT, value INTEGER);";
    rc = sqlite3_exec(db, create_table_sql, 0, 0, &err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    // Insert data into the table
    const char *insert_data_sql = "INSERT INTO data (name, value) VALUES ('example', 42);";
    rc = sqlite3_exec(db, insert_data_sql, 0, 0, &err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    const char *insert_data_sql_2 = "INSERT INTO data (name, value) VALUES ('blah', 100);";    
    rc = sqlite3_exec(db, insert_data_sql_2, 0, 0, &err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    const char *insert_3_begin = "INSERT INTO data (name, value) VALUES ('";
    
    const char *insert_3_end = "' , 95);";
    
    const char *firstHalf = concat_strings(insert_3_begin, json_str);

    const char *insert_data_sql_3 = concat_strings(firstHalf, insert_3_end);

    rc = sqlite3_exec(db, insert_data_sql_3, 0,0, &err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    // Query the data
    const char *select_data_sql = "SELECT * FROM data WHERE id = 6;";
    rc = sqlite3_exec(db, select_data_sql, callback, 0, &err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    rc = sqlite3_exec(db, select_data_sql, getJSONvalue, 0, &err_msg);

    // Close the database
    sqlite3_close(db);

    return 0;
}
