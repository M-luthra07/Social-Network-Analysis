// interactions.js

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('companySearch');
    let debounceTimer;

    // Create results container
    const resultsContainer = document.createElement('div');
    resultsContainer.className = 'list-group position-absolute w-100 shadow-lg';
    resultsContainer.style.zIndex = '1050';
    resultsContainer.style.display = 'none';
    resultsContainer.style.top = '100%';
    searchInput.parentNode.appendChild(resultsContainer);

    searchInput.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    resultsContainer.innerHTML = '';
                    if (data.results && data.results.length > 0) {
                        data.results.forEach(name => {
                            const item = document.createElement('a');
                            item.href = '#';
                            item.className = 'list-group-item list-group-item-action';
                            item.innerText = name;
                            item.addEventListener('click', (e) => {
                                e.preventDefault();
                                openCompanyModal(name); // Defined in network_viz.js
                                searchInput.value = '';
                                resultsContainer.style.display = 'none';
                            });
                            resultsContainer.appendChild(item);
                        });
                        resultsContainer.style.display = 'block';
                    } else {
                        resultsContainer.style.display = 'none';
                    }
                });
        }, 300);
    });

    // Close search results when clicking outside
    document.addEventListener('click', function (e) {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.style.display = 'none';
        }
    });
});
