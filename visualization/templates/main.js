// Set up dimensions
const width = 1800;
const height = 900;
const margin = {top: 20, right: 300, bottom: 30, left: 120};
const nodeSpacing = 100;  // Fixed spacing between nodes

// Create SVG
const svg = d3.select("#chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom);

const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Create zoom behavior
const zoom = d3.zoom()
    .scaleExtent([0.1, 10])
    .on("zoom", zoomed);

svg.call(zoom);

function zoomed(event) {
    g.attr("transform", event.transform);
}

// Zoom control buttons
d3.select("#zoom-in").on("click", () => {
    svg.transition().call(zoom.scaleBy, 1.5);
});

d3.select("#zoom-out").on("click", () => {
    svg.transition().call(zoom.scaleBy, 0.75);
});

d3.select("#reset-zoom").on("click", () => {
    svg.transition().call(zoom.transform, d3.zoomIdentity);
});

function updateVisualization(filterType, filterValue, layoutType) {
    // Clear existing visualization
    g.selectAll("*").remove();

    // Filter data based on selected filter
    const filteredData = filterData(data, filterType, filterValue);

    // Create hierarchical layout
    const root = d3.hierarchy(filteredData);

    if (layoutType === "tree") {
        createTreeLayout(root, g, width, height, nodeSpacing);
    } else if (layoutType === "force") {
        createForceLayout(root, g, width, height, nodeSpacing);
    }

    // Add tooltips
    addTooltips(g.selectAll(".node"));

    // Add rolling index nodes and links
    addRollingIndexNodesAndLinks(g, filterType, filterValue, width, height);
}

// Set up filter controls
const filterType = d3.select("#filterType");
const filterValue = d3.select("#filterValue");
const layoutType = d3.select("#layoutType");

filterType.on("change", function() {
    const selectedType = this.value;
    filterValue.html("");
    filterValue.append("option").attr("value", "all").text("All");

    if (selectedType === "none") {
        filterValue.property("disabled", true);
    } else {
        filterValue.property("disabled", false);
        if (selectedType === "rolling") {
            Object.keys(rollingIndices).forEach(pattern => {
                filterValue.append("option").attr("value", pattern).text(pattern);
            });
        } else if (selectedType === "index") {
            allIndices.forEach(index => {
                filterValue.append("option").attr("value", index).text(index);
            });
        }
    }

    updateVisualization(selectedType, "all", layoutType.property("value"));
});

filterValue.on("change", function() {
    updateVisualization(filterType.property("value"), this.value, layoutType.property("value"));
});

layoutType.on("change", function() {
    updateVisualization(filterType.property("value"), filterValue.property("value"), this.value);
});

// Initial visualization
updateVisualization("none", "all", "tree");
