(function(){"use strict";

const bits = 1<<14;
const min_ngram = 3;
const max_ngram = 4;

const utf8 = new TextEncoder();
const index_cache = Array(bits);
const search_field = document.getElementById("search_field");
const stuff = document.getElementById("stuff");
const footer = document.getElementById("footer");

async function load_index(i) {
	if(index_cache[i] !== undefined) return index_cache[i];
	const resource = fetch("index/"+i).then((x) => x.arrayBuffer())
	const result = new Uint32Array(await resource);
	index_cache[i] = result;
	return result;
}

function load_block(i) {
	return fetch("blocks/"+i).then((x) => x.json())
}

function ngram_code(data, start, length) {
	let x = 0;
	for(let i = 0; i < length; i++)
		x |= data[start+i] << 8*i;
	return x;
}

function mix32(x) {
	x ^= x >> 16;
	x = Math.imul(x, 0x7feb352d);
	x ^= x >> 15;
	x = Math.imul(x, 0x846ca68b);
	x ^= x >> 16;
	return x;
}

function increment(reg, width, a, mask) {
	for(let i = 0; mask && i < width; i++) {
		const A = reg[a + i];
		reg[a + i] ^= mask;
		mask &= A;
	}
}

function is_equal(reg, width, a, imm) {
	let result = -1;
	for(let i = 0; i < width; i++) {
		const A = reg[a + i];
		const B = ((imm >> i) & 1) - 1;
		result &= A ^ B;
	}
	return result;
}

function render_text(tag, text) {
	const node = document.createElement(tag);
	node.textContent = text;
	stuff.appendChild(node);
}

function render_product(i, product, matches, total) {
	render_text("h2", '#' + i + ' ' + product.name);
	render_text("h4", product.brand);
	render_text("p", 'matched '+matches+'/'+total+' n-grams');
	render_text("p", product.description);
}

function outofstuff() {
	if(window.pageYOffset + window.innerHeight >= stuff.offsetHeight)
		return;
	return new Promise((resolve, reject) => {
		const scroll = () => {
			if(window.pageYOffset + window.innerHeight >= stuff.offsetHeight) {
				window.removeEventListener("scroll", scroll);
				resolve();
			}
		};
		window.addEventListener("scroll", scroll);
	});
}

let hurglg = 0;

async function do_search(ev) {
	const hack = ++hurglg;
	stuff.innerHTML = '';
	
	const fetches = [];
	const unique_ngrams = new Set();
	const query = utf8.encode(search_field.value.toLowerCase());
	
	for(let n = min_ngram; n <= max_ngram; n++)
	for(let i = 0; i + n <= query.length; i++) {
		const ngram = ngram_code(query, i, n);
		if(unique_ngrams.has(ngram)) continue;
		fetches.push(load_index(bits - 1 & mix32(ngram)));
		fetches.push(load_index(bits - 1 & mix32(ngram ^ 0x16b33fb4)));
		fetches.push(load_index(bits - 1 & mix32(ngram ^ 0x59300865)));
		unique_ngrams.add(ngram);
	}
	
	if(unique_ngrams.size == 0)
		return;
	
	const indices = await Promise.all(fetches);
	if(hack != hurglg) return;
	
	for(let h = 0; h <= unique_ngrams.size; h++) {
		
		const value = unique_ngrams.size - h;
		const width = Math.ceil(Math.log2(unique_ngrams.size + 1)) | 0;
		
		for(let i = 0; i < indices[0].length; i++) {
			const counter = new Uint32Array(width);
			
			for(let j = 0; j < indices.length; j += 3) {
				const mask = indices[j][i] & indices[j+1][i] & indices[j+2][i];
				increment(counter, width, 0, mask);
			}
			
			const mask = is_equal(counter, width, 0, value);
			
			if(mask == 0)
				continue;
			
			await outofstuff();
			if(hack != hurglg) return;
			
			const block = await load_block(i);
			if(hack != hurglg) return;
			
			for(let j = 0; j < 32; j++)
			if((mask>>j)&1)
				render_product(i*32 + j, block[j], value, unique_ngrams.size);
		}
	}
}

search_field.addEventListener("input", do_search);
window.addEventListener("load", do_search);

})();