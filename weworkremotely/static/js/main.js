// --- 1. ESTADO ---
const state = {
    query: '',
    category: [],
    country: [],
    job_type: [],
    salary: [],
    skill: []
};

// Referencias a los elementos del DOM
const searchInput = document.getElementById('search-query');
const resultsContainer = document.getElementById('results-container');
const resultsCount = document.getElementById('results-count');
const loader = document.getElementById('loader');
const filterSidebar = document.getElementById('filter-sidebar'); 
// Listas de filtros
const filterLists = {
    category: document.getElementById('category-list'),
    country: document.getElementById('country-list'),
    job_type: document.getElementById('job-type-list'),
    salary: document.getElementById('salary-list'),
    skill: document.getElementById('skill-list')
};

// --- FUNCIÓN PRINCIPAL ---
async function fetchResults() {
    if (loader) loader.style.display = 'block';

    // CONSTRUCCIÓN DE URL
    const params = new URLSearchParams({ q: state.query });
    ['category', 'country', 'job_type', 'salary', 'skill'].forEach(key => {
        state[key].forEach(value => {
            params.append(key, value);
        });
    });
    const url = `/api/search?${params.toString()}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
        
        const data = await response.json();

        // 1. Renderizar los resultados centrales
        renderResults(data.hits);
        if (resultsCount) resultsCount.innerText = `Found ${data.total} results.`;

        // 2. MEMORIZA EL DESPLAZAMIENTO DE LA BARRA LATERAL ANTES DE ACTUALIZAR
        const scrollPos = filterSidebar ? filterSidebar.scrollTop : 0;

        // 3. RENDERIZA LOS FILTROS (con ordenación A-Z)
        renderFilterList(filterLists.category, data.categories.buckets, 'category', 'category', 'All categories');
        renderFilterList(filterLists.country, data.countries.buckets, 'country', 'country', 'All countries');
        renderFilterList(filterLists.job_type, data.job_types.buckets, 'job_type', 'job-type', 'All types');
        renderFilterList(filterLists.salary, data.salaries.buckets, 'salary', 'salary', 'All salaries');
        renderFilterList(filterLists.skill, data.skills.buckets, 'skill', 'skill', 'All skills');

        // 4. RESTABLECE EL DESPLAZAMIENTO
        if (filterSidebar) filterSidebar.scrollTop = scrollPos;

    } catch (error) {
        console.error("Fetch error:", error);
        if (resultsContainer) resultsContainer.innerHTML = '<p style="color: red;">Error loading data.</p>';
    } finally {
        if (loader) loader.style.display = 'none';
    }
}

// --- RENDERIZAR RESULTADOS (TARJETA) ---
function renderResults(hits) {
    if (!resultsContainer) return;
    if (hits.length === 0) {
        resultsContainer.innerHTML = '<p>No results found.</p>';
        return;
    }
    const cardsHtml = hits.map(hit => {
        const job = hit._source;
        const skillsHtml = (job.skills || []).slice(0, 20).map(skill => `<span>${skill}</span>`).join('');
        
        let descriptionHtml = '';
        if (hit.highlight && hit.highlight.description) {
            descriptionHtml = `<div class="snippet">...${hit.highlight.description[0]}...</div>`;
        } else if (job.description) {
            descriptionHtml = `<div class="snippet">${job.description.substring(0, 150)}...</div>`;
        }
        
        const postedDate = job.posted_date ? job.posted_date.split('T')[0] : 'N/A';
        const logoHtml = job.logo_url
            ? `<img src="${job.logo_url}" alt="${job.company} logo" class="company-logo">`
            : `<div class="company-logo-placeholder">${job.company ? job.company.charAt(0) : 'J'}</div>`;
            
        return `
            <div class="result">
                <div class="result-header">
                    ${logoHtml}
                    <div class="result-info">
                        <h3><a href="${job.url}" target="_blank">${job.title}</a></h3>
                        <div class="meta">
                            <strong>Company:</strong> ${job.company || 'N/A'} | 
                            <strong>Type:</strong> ${job.job_type || 'N/A'} |
                            <strong>Date:</strong> ${postedDate}
                        </div>
                    </div>
                </div>
                ${skillsHtml ? `<div class="skills">${skillsHtml}</div>` : ''}
                ${descriptionHtml}
            </div>
        `;
    }).join(''); 
    resultsContainer.innerHTML = cardsHtml;
}

// --- RENDERIZAR FILTROS (ESTABLE A-Z) ---
function renderFilterList(listElement, buckets, stateKey, dataKey, allText) {
    if (!listElement) return;

    // A. Mapa de resultados de la API
    const bucketMap = new Map(buckets.map(b => [b.key, b.doc_count]));

    // B. Unión de claves API + Seleccionados (para que no desaparezcan los activos con 0 resultados)
    const allKeys = new Set([...bucketMap.keys(), ...state[stateKey]]);

    // C. Creación de objetos
    let items = Array.from(allKeys).map(key => {
        return {
            key: key,
            isActive: state[stateKey].includes(key)
        };
    });

    // D. ORDENACIÓN A-Z (Case Insensitive)
    // Este es el corazón de la estabilidad: ignora los números, mira solo el nombre.
    items.sort((a, b) => a.key.toLowerCase().localeCompare(b.key.toLowerCase()));

    // E. Generación de HTML
    let filtersHtml = `
        <li>
            <a data-${dataKey}="" 
               class="${state[stateKey].length === 0 ? 'active' : ''}">
                ${allText}
            </a>
        </li>
    `;

    filtersHtml += items.map(item => {
        if (!item.key) return ''; 
        
        return `
        <li>
            <a data-${dataKey}="${item.key}" 
               class="${item.isActive ? 'active' : ''}"> 
                ${item.key}
            </a>
        </li>
    `}).join('');

    listElement.innerHTML = filtersHtml;
}

// --- HELPER: BÚSQUEDA LOCAL ---
function addClientSideListFilter(inputId, listId) {
    const input = document.getElementById(inputId);
    const list = document.getElementById(listId);
    if (!input || !list) return;
    
    input.addEventListener('keyup', () => {
        const searchTerm = input.value.toLowerCase();
        const listItems = list.getElementsByTagName('li');
        for (let i = 0; i < listItems.length; i++) {
            const li = listItems[i];
            const link = li.querySelector('a');
            if (link) {
                const text = link.textContent.toLowerCase();
                const isAllLink = (link.getAttribute(`data-${inputId.replace('-search','')}`) === "") || (Object.values(link.dataset)[0] === "");
                if (isAllLink || text.includes(searchTerm)) {
                    li.style.display = "";
                } else {
                    li.style.display = "none";
                }
            }
        }
    });
}

function toggleFilter(array, value) {
    const index = array.indexOf(value);
    if (index > -1) {
        array.splice(index, 1);
    } else {
        array.push(value);
    }
}

// --- EVENT LISTENERS ---
document.addEventListener('DOMContentLoaded', () => {
    fetchResults();

    // Acordeón de barra lateral
    const sidebarHeaders = document.querySelectorAll('aside h3');
    sidebarHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const inputField = header.nextElementSibling;
            const list = inputField.nextElementSibling;
            if (list && list.tagName === 'UL') {
                list.style.display = (list.style.display === 'block') ? 'none' : 'block';
            }
        });
    });

    // Foco en el input
    const inputs = document.querySelectorAll('aside input[type="text"]');
    inputs.forEach(input => {
        input.addEventListener('focus', (e) => {
            const list = e.target.nextElementSibling;
            if (list && list.tagName === 'UL') {
                list.style.display = 'block';
            }
        });
    });

    // Filtros de texto
    addClientSideListFilter('category-search', 'category-list');
    addClientSideListFilter('country-search', 'country-list');
    addClientSideListFilter('salary-search', 'salary-list');
    addClientSideListFilter('skill-search', 'skill-list');
    addClientSideListFilter('job-type-search', 'job-type-list');

    // Búsqueda principal
    let debounceTimer;
    if (searchInput) {
        searchInput.addEventListener('keyup', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                state.query = searchInput.value;
                fetchResults();
            }, 300);
        });
    }
});

// Manejador de clics en filtros
if (filterSidebar) {
    filterSidebar.addEventListener('click', (event) => {
        const target = event.target.closest('a');
        if (!target) return;
        event.preventDefault();

        const map = {'category': 'category', 'country': 'country', 'jobType': 'job_type', 'salary': 'salary', 'skill': 'skill'};
        let foundKey = null;
        for (const key in map) {
            if (target.dataset[key] !== undefined) {
                foundKey = key;
                break;
            }
        }

        if (foundKey) {
            const stateKey = map[foundKey];
            const value = target.dataset[foundKey];
            if (value === "") {
                state[stateKey] = [];
            } else {
                toggleFilter(state[stateKey], value);
            }
            fetchResults();
        }
    });
}
