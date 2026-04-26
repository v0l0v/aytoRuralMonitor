document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab-btn');
    const dynamicFilters = document.getElementById('dynamic-filters');
    const searchBtn = document.getElementById('search-btn');
    const btnText = searchBtn.querySelector('.btn-text');
    const loader = searchBtn.querySelector('.loader');
    const resultsSection = document.getElementById('results-section');
    const cardsContainer = document.getElementById('cards-container');
    const resultsCount = document.getElementById('results-count');
    const resultsTitle = document.getElementById('results-title');
    const modal = document.getElementById('call-modal');
    const closeModalBtn = document.getElementById('close-modal');

    let currentScope = 'national';
    let geographyData = {};
    let currentCalls = [];

    // Cargar datos geográficos
    fetch('/api/geography')
        .then(res => res.json())
        .then(data => {
            geographyData = data;
        })
        .catch(err => console.error("Error loading geography:", err));

    // Cambiar de pestaña
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentScope = tab.dataset.scope;
            renderFilters(currentScope);
        });
    });

    // Renderizar filtros según el ámbito
    function renderFilters(scope) {
        dynamicFilters.innerHTML = '';
        
        if (scope === 'national') {
            dynamicFilters.innerHTML = `<p style="color: var(--text-muted); font-size: 0.875rem;">Buscando en todas las convocatorias nacionales.</p>`;
        } 
        else if (scope === 'regional') {
            const select = document.createElement('select');
            select.id = 'ccaa-select';
            Object.keys(geographyData).sort().forEach(ccaa => {
                const option = document.createElement('option');
                option.value = ccaa;
                option.textContent = ccaa;
                select.appendChild(option);
            });
            
            const group = document.createElement('div');
            group.className = 'input-group';
            group.innerHTML = `<label for="ccaa-select">Comunidad Autónoma</label>`;
            group.appendChild(select);
            dynamicFilters.appendChild(group);
        }
        else if (scope === 'provincial') {
            const ccaaGroup = document.createElement('div');
            ccaaGroup.className = 'input-group';
            ccaaGroup.innerHTML = `<label for="ccaa-select">Comunidad Autónoma</label>`;
            
            const ccaaSelect = document.createElement('select');
            ccaaSelect.id = 'ccaa-select';
            Object.keys(geographyData).sort().forEach(ccaa => {
                const option = document.createElement('option');
                option.value = ccaa;
                option.textContent = ccaa;
                ccaaSelect.appendChild(option);
            });
            ccaaGroup.appendChild(ccaaSelect);
            
            const provGroup = document.createElement('div');
            provGroup.className = 'input-group';
            provGroup.innerHTML = `<label for="prov-select">Provincia</label>`;
            const provSelect = document.createElement('select');
            provSelect.id = 'prov-select';
            provGroup.appendChild(provSelect);

            dynamicFilters.appendChild(ccaaGroup);
            dynamicFilters.appendChild(provGroup);

            // Actualizar provincias al cambiar CCAA
            const updateProv = () => {
                const ccaa = ccaaSelect.value;
                provSelect.innerHTML = '';
                if(geographyData[ccaa]) {
                    geographyData[ccaa].sort().forEach(prov => {
                        const option = document.createElement('option');
                        option.value = prov;
                        option.textContent = prov;
                        provSelect.appendChild(option);
                    });
                }
            };
            ccaaSelect.addEventListener('change', updateProv);
            updateProv(); // init
        }
        else if (scope === 'free') {
            const group = document.createElement('div');
            group.className = 'input-group';
            group.innerHTML = `
                <label for="free-search">Palabra clave</label>
                <input type="text" id="free-search" placeholder="Ej: energía solar, digitalización..." />
            `;
            dynamicFilters.appendChild(group);
        }
    }

    // Inicializar filtros
    renderFilters(currentScope);

    // Buscar
    searchBtn.addEventListener('click', () => {
        let term = '';
        
        if (currentScope === 'regional') {
            term = document.getElementById('ccaa-select').value;
        } else if (currentScope === 'provincial') {
            term = document.getElementById('prov-select').value;
        } else if (currentScope === 'free') {
            term = document.getElementById('free-search').value;
            if (!term) return alert("Escribe un término de búsqueda");
        }

        // UI Loading State
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        searchBtn.disabled = true;
        resultsSection.classList.add('hidden');
        cardsContainer.innerHTML = '';

        const strictFilter = document.getElementById('strict-filter-toggle').checked;

        fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                scope: currentScope, 
                term: term,
                strict_filter: strictFilter
            })
        })
        .then(res => res.json())
        .then(data => {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            searchBtn.disabled = false;

            if (data.success) {
                currentCalls = data.calls;
                renderResults(currentCalls, currentScope === 'national' ? 'España' : term);
            } else {
                alert("Error al buscar: " + data.error);
            }
        })
        .catch(err => {
            console.error(err);
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            searchBtn.disabled = false;
            alert("Error de conexión");
        });
    });

    function renderResults(calls, term) {
        resultsSection.classList.remove('hidden');
        resultsCount.textContent = calls.length;
        resultsTitle.textContent = `Resultados para ${term}`;
        
        if (calls.length === 0) {
            cardsContainer.innerHTML = `<p style="color: var(--text-muted); grid-column: 1/-1; text-align: center; padding: 2rem;">No se han encontrado convocatorias activas para esta búsqueda.</p>`;
            return;
        }

        // Helper to parse date "dd/mm/yyyy"
        const parseDate = (dateStr) => {
            if (!dateStr || !dateStr.includes('/')) return new Date(0); // For sorting purposes, "Sin fecha" goes to bottom
            const parts = dateStr.split('/');
            if (parts.length !== 3) return new Date(0);
            return new Date(parts[2], parts[1] - 1, parts[0]);
        };

        // Sort calls descending by date
        calls.sort((a, b) => parseDate(b.deadline).getTime() - parseDate(a.deadline).getTime());

        // Group by year
        const groupedCalls = {};
        calls.forEach(call => {
            let year = "Sin fecha definida";
            if (call.deadline && call.deadline.includes('/')) {
                const parts = call.deadline.split('/');
                if (parts.length === 3) year = parts[2];
            }
            if (!groupedCalls[year]) groupedCalls[year] = [];
            groupedCalls[year].push(call);
        });

        // Sort years descending
        const sortedYears = Object.keys(groupedCalls).sort((a, b) => {
            if (a === "Sin fecha definida") return 1;
            if (b === "Sin fecha definida") return -1;
            return parseInt(b) - parseInt(a);
        });

        cardsContainer.innerHTML = '';
        let globalIndex = 0;

        sortedYears.forEach(year => {
            // Inject year header
            const header = document.createElement('h2');
            header.className = 'year-header';
            header.textContent = year;
            cardsContainer.appendChild(header);

            // Inject cards for this year
            groupedCalls[year].forEach((call) => {
                const delay = (globalIndex % 10) * 0.1; // reset delay to avoid extremely long animations
                const card = document.createElement('div');
                card.className = 'card';
                card.style.animationDelay = `${delay}s`;
                
                card.innerHTML = `
                    <h3 class="card-title" title="${call.title}">${call.title}</h3>
                    <div class="card-meta">
                        <span class="meta-item">💰 ${call.budget}</span>
                        <span class="meta-item">📅 ${call.deadline}</span>
                    </div>
                    <p class="card-desc">${call.summary}</p>
                    <div class="card-actions">
                        <button class="link-btn view-more-btn" data-index="${globalIndex}" style="background:none; border:none; cursor:pointer; font-family:inherit;">Ver más...</button>
                        <button class="secondary-btn notify-btn" data-index="${globalIndex}">
                            📲 Notificar
                        </button>
                    </div>
                `;
                cardsContainer.appendChild(card);
                globalIndex++;
            });
        });

        // Add Notify Listeners
        document.querySelectorAll('.notify-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.currentTarget.dataset.index;
                const callToNotify = calls[idx];
                
                e.currentTarget.innerHTML = 'Enviando...';
                e.currentTarget.disabled = true;

                fetch('/api/notify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(callToNotify)
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        e.currentTarget.innerHTML = '✅ Enviado';
                        showToast();
                    } else {
                        e.currentTarget.innerHTML = '❌ Error';
                        e.currentTarget.disabled = false;
                    }
                })
                .catch(() => {
                    e.currentTarget.innerHTML = '❌ Error';
                    e.currentTarget.disabled = false;
                });
            });
        });

        // Add View More Listeners
        document.querySelectorAll('.view-more-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = e.currentTarget.dataset.index;
                const call = calls[idx];
                openModal(call, idx);
            });
        });
    }

    function openModal(call, index) {
        document.getElementById('modal-title').textContent = call.title;
        document.getElementById('modal-budget').textContent = `💰 ${call.budget}`;
        document.getElementById('modal-deadline').textContent = `📅 ${call.deadline}`;
        document.getElementById('modal-desc').textContent = call.summary;
        document.getElementById('modal-url').href = call.url;
        
        const notifyBtn = document.getElementById('modal-notify-btn');
        notifyBtn.dataset.index = index;
        notifyBtn.innerHTML = '📲 Notificar al Alcalde';
        notifyBtn.disabled = false;

        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Evitar scroll del fondo
    }

    closeModalBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
        }
    });

    // Notify logic for Modal button
    document.getElementById('modal-notify-btn').addEventListener('click', (e) => {
        const idx = e.currentTarget.dataset.index;
        const callToNotify = currentCalls[idx];
        
        e.currentTarget.innerHTML = 'Enviando...';
        e.currentTarget.disabled = true;

        fetch('/api/notify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(callToNotify)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                e.currentTarget.innerHTML = '✅ Enviado';
                showToast();
            } else {
                e.currentTarget.innerHTML = '❌ Error';
                e.currentTarget.disabled = false;
            }
        })
        .catch(() => {
            e.currentTarget.innerHTML = '❌ Error';
            e.currentTarget.disabled = false;
        });
    });

    function showToast() {
        const toast = document.getElementById('toast');
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }
});
