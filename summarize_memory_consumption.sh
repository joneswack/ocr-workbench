#!/bin/sh

awk '
$1 == "MEM" {
    if ($3 > max) max = $3
}
END {
    if (max > 0)
        print max / (1024 * 1024)
}
'
