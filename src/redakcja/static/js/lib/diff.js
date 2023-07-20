$.wiki.diff = function(a, b) {
    MAXD = 500;

    let VV = new Array(),
        N = a.length,
        M = b.length,
        V, Vp, D, x, y, k;
    V = VV[-1] = Array();
    V[1] = 0;
    let endD = null;
    for (D = 0; D < MAXD && endD === null; D++) {
        Vp = V;
        V = VV[D] = Array();
        for (k = -D; k <= D; k += 2) {
            if (k == -D || (k != D && Vp[k-1] < Vp[k + 1])) {
                x = Vp[k + 1];
            } else {
                x = Vp[k - 1] + 1;
            }
            y = x - k;

            while (x < N && y < M && a[x] == b[y]) {
                x ++;
                y ++;

                // Avoid comparing long text character by character.
                let step = 1;
                while (true) {
                    step = Math.min(step * 2, N - x, M - y);
                    if (!step) break;
                    if (a.substr(x, step) == b.substr(y, step)) {
                        x += step;
                        y += step;
                    } else {
                        break;
                    }
                }
            }

            V[k] = x;
            if (x == N && y == M) {
                endD = D;
                break;
            }
        }
    }
    if (endD === null) {
        // Max D limit reached, diff too big. Bail and just return the whole target text.
        return b;
    }

    // Now go back.
    result = []
    let px, py;
    for (D = endD; D; --D) {
        k = x - y;
        V = VV[D - 1];
        if (V[k - 1] === undefined || V[k + 1] > V[k - 1]) {
            // move up
            k ++;
            px = V[k];
            py = px - k;
            if (result.length && result[0][0] && result[0][1] == px) {
                result[0][2] = b[py] + result[0][2];
            } else {
                result.unshift(
                    [true, px, b[py]]
                )
            }
        } else {
            // move down
            k --;
            px = V[k];
            py = px - k;
            if (result.length && !result[0][0] && result[0][1] == px + 1) {
                result[0][1]--;
                result[0][2]++;
            } else {
                result.unshift(
                    [false, px, 1]
                )
            }
        }
        x = px;
        y = py;
    }
    return result
}


$.wiki.patch = function(a, p) {
    for (i = p.length - 1; i >= 0; -- i) {
        let c = p[i];
        if (c[0]) {
            a = a.substr(0, c[1]) + c[2] + a.substr(c[1]);
        } else {
            a = a.substr(0, c[1]) + a.substr(c[1] + c[2]);
        }
    }
    return a;
}
