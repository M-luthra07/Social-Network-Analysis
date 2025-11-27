// network_viz.js

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('network-container');
    
    // Fetch network data
    fetch('/api/network')
        .then(response => response.json())
        .then(data => {
            const nodes = new vis.DataSet(data.nodes);
            const edges = new vis.DataSet(data.edges);
            
            const networkData = {
                nodes: nodes,
                edges: edges
            };
            
            const options = {
                nodes: {
                    shape: 'dot',
                    size: 16,
                    font: {
                        size: 14,
                        color: '#2b2d42',
                        face: 'Outfit'
                    },
                    borderWidth: 2,
                    shadow: true
                },
                edges: {
                    width: 1,
                    color: { inherit: 'from', opacity: 0.3 },
                    smooth: {
                        type: 'continuous'
                    }
                },
                physics: {
                    stabilization: false,
                    barnesHut: {
                        gravitationalConstant: -8000,
                        springConstant: 0.04,
                        springLength: 95
                    }
                },
                interaction: {
                    hover: true,
                    tooltipDelay: 200,
                    hideEdgesOnDrag: true
                }
            };
            
            const network = new vis.Network(container, networkData, options);
            
            // Handle click
            network.on("click", function (params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    openCompanyModal(nodeId);
                }
            });
        })
        .catch(err => console.error("Error loading network:", err));
});

function openCompanyModal(companyName) {
    const modalTitle = document.getElementById('modalCompanyName');
    const modalBody = document.getElementById('modalCompanyBody');
    
    // Show modal
    const myModal = new bootstrap.Modal(document.getElementById('companyModal'));
    myModal.show();
    
    modalTitle.innerText = companyName;
    modalBody.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    
    // Fetch details
    fetch(`/api/company/${encodeURIComponent(companyName)}`)
        .then(res => {
            if (!res.ok) throw new Error("Not found");
            return res.json();
        })
        .then(data => {
            let html = '<ul class="list-group list-group-flush">';
            for (const [key, value] of Object.entries(data)) {
                if (key !== "Company_Name") { // Name already in title
                    html += `
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            <span class="fw-bold text-muted small text-uppercase">${key.replace(/_/g, ' ')}</span>
                            <span>${value}</span>
                        </li>
                    `;
                }
            }
            html += '</ul>';
            modalBody.innerHTML = html;
        })
        .catch(err => {
            modalBody.innerHTML = '<p class="text-danger">Error loading details.</p>';
        });
}
