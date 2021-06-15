#include <sys/time.h>
#include <sys/resource.h>
#include <stdlib.h>
#include <signal.h>


int main() {
    // The rlimit struct has 2 fields:
    // - rlim_cur: Current limit, can be set by other processes as well.
    // - rlim_max: Upper bound that the rlim_cur can be set to.
    //
    // We want both of them to be 0 so our process will not be able to write any files.
    struct rlimit file_size_limit;
    file_size_limit.rlim_cur = 0;
    file_size_limit.rlim_max = 0;

    // Set the limit on RLIMIT_FSIZE
    setrlimit(RLIMIT_FSIZE, &file_size_limit);

    // By default, when the limit is reached, SIGXFSZ is sent to the process and it gets
    // killed. We want to ignore this signal for the app to continue even after the failure.
    signal(SIGXFSZ, SIG_IGN);

    // The passcode is 0 since 0 bytes will be written to the file.
    system("/home/otp/otp 0");
}
