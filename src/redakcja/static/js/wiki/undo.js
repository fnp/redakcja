{

    class Undo {
        maxItems = 100;
        stack = [];
        position = 0;

        stats = {size: 0};

        constructor() {
            $(() => {
                this.$undo = $("#undoBtn");
                this.$undo.on('click', () => {CurrentDocument.undo();})
                this.$redo = $("#redoBtn");
                this.$redo.on('click', () => {CurrentDocument.redo();})
                this.$stats = $("#undoStats");
            })
        }

        refresh() {
            this.$undo.prop('disabled', !this.canUndo);
            this.$redo.prop('disabled', !this.canRedo);
            this.$undo.attr('title', 'undo\n\n' + this.renderStats())
        }

        renderStats() {
            return this.stats.size / 1e6;
        }

        push(state) {
            // Has the state actually changed?
            if (state == this.materialize(this.position))
                return;

            while (this.position) {
                this.pop();
                --this.position;
            }

            this.put(state);
            this.trim();
            this.refresh();
        }
        pop() {
            this.stats.size -= this.stack[0].length;
            return this.stack.shift()
        }
        put(state) {
            this.stack.unshift(state);
            this.stats.size += state.length;
        }
        trim() {
            while (this.stack.length > this.maxItems) {
                this.stats.size -= this.stack.pop().length;
            }
        }
        materialize(n) {
            return this.stack[n];
        }

        undo() {
            if (!this.canUndo) return;
            let val = this.materialize(++this.position);
            this.refresh();
            return val;
        }

        redo() {
            if (!this.canRedo) return;
            let val = this.materialize(--this.position);
            this.refresh();
            return val;
        }

        get canUndo() {
            return this.stack.length > this.position + 1;
        }

        get canRedo() {
            return this.position > 0;
        }
    }


    class TextUndo extends Undo {
        stats = {
            Items: 0,
            Size: 0,
            textSize: 0,
            textItems: 0,
            diffSize: 0,
            diffItems: 0,
            diffChanges: 0,
        }

        statsFor(item) {
            if (Array.isArray(item)) {
                return {
                    diffItems: 1,
                    diffChanges: item.length,
                    diffSize: JSON.stringify(item).length
                }
            } else {
                return {
                    textItems: 1,
                    textSize: item.length
                }
            }
        }
        addStats(stats) {
            for (let i in stats) {
                this.stats[i] += stats[i]
            }
        }
        subStats(stats) {
            for (let i in stats) {
                this.stats[i] -= stats[i]
            }
        }
        renderStats() {
            this.stats['Items'] = this.stats['textItems'] + this.stats['diffItems'];
            this.stats['Size'] = this.stats['textSize'] + this.stats['diffSize'];
            let stats = '', v;
            for (let k in this.stats) {
                v = this.stats[k];
                if (k.endsWith('Size')) {
                    let level = 0;
                    while (v > 1000) {
                        v /= 1000;
                        level++;
                    }
                    v = Math.round(v)
                    v += ['B', 'kB', 'MB', 'GB'][level];
                }
                stats += k + ': ' + v + '\n';
            }
            return stats;
        }


        put(state) {
            if (this.stack.length) {
                let tip = this.materialize(0);
                this.subStats(this.statsFor(this.stack[0]))
                this.stack[0] = $.wiki.diff(state, tip);
                this.addStats(this.statsFor(this.stack[0]))
            }
            this.stack.unshift(state);
            this.addStats(this.statsFor(state));
        }
        pop() {
            if (this.stack.length > 1) {
                this.subStats(this.statsFor(this.stack[1]))
                this.stack[1] = this.materialize(1);
                this.addStats(this.statsFor(this.stack[1]))
            }
            this.subStats(this.statsFor(this.stack[0]))
            return this.stack.shift();
        }
        trim() {
            while (this.stack.length > this.maxItems) {
                this.subStats(this.statsFor(
                    this.stack.pop()
                ));
            }
        }

        materialize(n) {
            if (n >= this.stack.length) return;
            let state, base_i, i;
            for (i = 0; i <= n; ++i) {
                if (!Array.isArray(this.stack[i])) {
                    base_i = i;
                }
            }
            state = this.stack[base_i];
            for (i = base_i + 1; i <= n; ++i) {
                state = $.wiki.patch(state, this.stack[i]);
            }
            return state;
        }
    }

    $.wiki.undo = new TextUndo();
}
