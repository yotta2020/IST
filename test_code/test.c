int main() {
    int sum = 0;
    int num = 10;
    for (int i = 1; i <= num; i++) {
        if (i != 5 && i < 8) {
            sum += i;
        } else if (i == 8) {
            sum -= i;
        }
    }
    int j = 1;
    int limit = 5;
    while (j <= limit) {
        if (j > 2 && j != 4) {
            sum += j;
        }
        j++;
    }
    return 0;
}