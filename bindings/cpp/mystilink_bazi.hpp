#ifndef MYSTILINK_BAZI_HPP
#define MYSTILINK_BAZI_HPP

#include "../c/mystilink_bazi.h"

#include <stdexcept>
#include <string>
#include <vector>

namespace mystilink {
namespace bazi {

inline std::string run(const std::vector<std::string> &args) {
    std::vector<const char *> argv;
    argv.reserve(args.size());
    for (const auto &a : args) {
        argv.push_back(a.c_str());
    }
    char err[512];
    err[0] = '\0';
    char *json = mystilink_bazi_run(static_cast<int>(argv.size()), argv.data(), err, sizeof(err));
    if (!json) {
        throw std::runtime_error(err[0] ? err : "mystilink_bazi_run failed");
    }
    std::string out(json);
    mystilink_bazi_free(json);
    return out;
}

inline std::string calculate(const std::string &date, int hour = 11, int minute = 0) {
    char err[512];
    err[0] = '\0';
    char *json = mystilink_bazi_calculate(date.c_str(), hour, minute, nullptr, 0.0, 0, err, sizeof(err));
    if (!json) {
        throw std::runtime_error(err[0] ? err : "calculate failed");
    }
    std::string out(json);
    mystilink_bazi_free(json);
    return out;
}

inline std::string dayun(const std::string &date, const std::string &gender, int count = 8) {
    char err[512];
    err[0] = '\0';
    char *json = mystilink_bazi_dayun(date.c_str(), gender.c_str(), count, err, sizeof(err));
    if (!json) {
        throw std::runtime_error(err[0] ? err : "dayun failed");
    }
    std::string out(json);
    mystilink_bazi_free(json);
    return out;
}

inline std::string liunian(int year, const std::string &day_stem = "") {
    char err[512];
    err[0] = '\0';
    char *json = mystilink_bazi_liunian(
        year,
        day_stem.empty() ? nullptr : day_stem.c_str(),
        nullptr,
        err,
        sizeof(err)
    );
    if (!json) {
        throw std::runtime_error(err[0] ? err : "liunian failed");
    }
    std::string out(json);
    mystilink_bazi_free(json);
    return out;
}

}  // namespace bazi
}  // namespace mystilink

#endif
