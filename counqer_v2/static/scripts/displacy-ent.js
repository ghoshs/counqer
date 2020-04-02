//- ----------------------------------
//- 💥 DISPLACY ENT
//- ----------------------------------

'use strict';

class displaCyENT {
    constructor (options) {
        // this.api = api;
        this.container = options.container || document.querySelector('#displacy');

        this.defaultText = options.defaultText || 'When Sebastian Thrun started working on self-driving cars at Google in 2007, few people outside of the company took him seriously.';
        this.defaultModel = options.defaultModel || 'en';
        this.defaultEnts = options.defaultEnts || ['person', 'org', 'gpe', 'loc', 'product'];

        this.onStart = options.onStart || false;
        this.onSuccess = options.onSuccess || false;
        this.onError = options.onError || false;
        this.onRender = options.onRender || false;

    }

    parse(text = this.defaultText, model = this.defaultModel, ents = this.defaultEnts) {
        if(typeof this.onStart === 'function') this.onStart();

        let xhr = new XMLHttpRequest();
        xhr.open('POST', this.api, true);
        xhr.setRequestHeader('Content-type', 'text/plain');
        xhr.onreadystatechange = () => {
            if(xhr.readyState === 4 && xhr.status === 200) {
                if(typeof this.onSuccess === 'function') this.onSuccess();
                this.render(text, JSON.parse(xhr.responseText), ents);
            }

            else if(xhr.status !== 200) {
                if(typeof this.onError === 'function') this.onError(xhr.statusText);
            }
        }

        xhr.onerror = () => {
            xhr.abort();
            if(typeof this.onError === 'function') this.onError();
        }

        xhr.send(JSON.stringify({ text, model }));
    }

    render(text, spans, type, ents=['person', 'norp', 'fac', 'org', 'gpe', 'loc', 'product', 'event', 'work_of_art', 'law', 'language', 'cardinal']) {
        this.container.innerHTML = '';
        let offset = 0;

        spans.forEach(({ label, start, end, ent_sim}, idx) => {
            const entity = text.slice(start, end);
            const fragments = text.slice(offset, start).split('\n');

            fragments.forEach((fragment, i) => {
                this.container.appendChild(document.createTextNode(fragment));
                if(fragments.length > 1 && i != fragments.length - 1) this.container.appendChild(document.createElement('br'));
            });

            if (type === 'all_matches' || type === 'query') {
                if(ents.includes(label.toLowerCase())) {
                    const mark = document.createElement('mark');
                    mark.setAttribute('data-entity', label.toLowerCase());
                    if(type === 'all_matches'){
                        mark.setAttribute('title', ent_sim.toString());
                    }   
                    mark.appendChild(document.createTextNode(entity));
                    this.container.appendChild(mark);
                }

                else {
                    this.container.appendChild(document.createTextNode(entity));
                }
            }
            else {
                if((ents.includes(label.toLowerCase()) && ent_sim > 0) || (label.toLowerCase() === 'cardinal')) {
                    const mark = document.createElement('mark');
                    mark.setAttribute('data-entity', label.toLowerCase());
                    mark.setAttribute('title', ent_sim.toString());
                    mark.appendChild(document.createTextNode(entity));
                    this.container.appendChild(mark);
                }

                else {
                    this.container.appendChild(document.createTextNode(entity));
                }
            }
            

            offset = end;
        });

        this.container.appendChild(document.createTextNode(text.slice(offset, text.length)));

        // console.log(`%c💥  HTML markup\n%c<div class="entities">${this.container.innerHTML}</div>`, 'font: bold 16px/2 arial, sans-serif', 'font: 13px/1.5 Consolas, "Andale Mono", Menlo, Monaco, Courier, monospace');

        if(typeof this.onRender === 'function') this.onRender();
    }
}
