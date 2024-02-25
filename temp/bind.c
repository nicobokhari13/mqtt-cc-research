#include <stdio.h>
#include <sqlite3.h>

int main() {
    sqlite3 *db;
    char *err_msg = 0;

    // Open the database (creates a new one if it doesn't exist)
    int rc = sqlite3_open("example.db", &db);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 1;
    }

    // Prepare SQL statement
    const char *sql = "UPDATE your_table_name SET latencyQos = ? WHERE id = ?";
    sqlite3_stmt *stmt;

    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, 0);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 1;
    }

    // Bind parameters
    int id = 1; // id value to update
    int new_latencyQos = 42; // new value for latencyQos
    sqlite3_bind_int(stmt, 1, new_latencyQos); // Bind new_latencyQos to the first parameter
    sqlite3_bind_int(stmt, 2, id); // Bind id to the second parameter

    // Execute SQL statement
    rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        fprintf(stderr, "Failed to execute statement: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 1;
    }

    // Finalize statement and close the database
    sqlite3_finalize(stmt);
    sqlite3_close(db);

    printf("Update successful!\n");

    return 0;
}
