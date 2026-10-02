# 仅删除 JSON 字符串外的格式空白；保留字符串、转义、数字及 token 原字节。
# 这是固定 smoke 输出的词法比较器，不是通用 JSON 解析器/语义规范化器。
function fail(message) {
    print "json-compact: " message > "/dev/stderr"
    failed = 1
    exit 2
}
{
    for (i = 1; i <= length($0); i++) {
        c = substr($0, i, 1)
        if (in_string) {
            if (c ~ /[[:cntrl:]]/) fail("unescaped control character in string")
            printf "%s", c
            if (escaped) escaped = 0
            else if (c == "\\") escaped = 1
            else if (c == "\"") in_string = 0
        } else if (c == "\"") {
            in_string = 1
            seen = 1
            printf "%s", c
        } else if (c != " " && c != "\t" && c != "\r") {
            if (c ~ /[[:cntrl:]]/) fail("invalid whitespace outside string")
            seen = 1
            printf "%s", c
        }
    }
    # JSON 字符串不能含原始换行；不允许跨行拼接掩盖损坏。
    if (in_string) fail("unterminated string or raw newline")
}
END {
    if (failed) exit 2
    if (!seen) fail("empty input")
    printf "\n"
}
