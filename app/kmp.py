def kmp_search(text, pattern):
    # calculate the longest prefix suffix
    def compute_lps(pattern):
        lps = [0] * len(pattern)
        length = 0  # length of the previous longest prefix suffix
        i = 1
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    # KMP search algorithm
    lps = compute_lps(pattern)
    i = 0
    j = 0

    # search the pattern
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1

        # find the pattern
        if j == len(pattern):
            return True
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    # not found
    return False
