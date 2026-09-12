#include <iostream>
#include <string>

#include "../../bindings/cpp/mystilink_bazi.hpp"

int main() {
    try {
        std::string json = mystilink::bazi::calculate("1990-05-15", 12, 0);
        std::cout << json << std::endl;
    } catch (const std::exception &ex) {
        std::cerr << "error: " << ex.what() << std::endl;
        return 1;
    }
    return 0;
}
