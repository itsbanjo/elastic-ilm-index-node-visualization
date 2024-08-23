function filterData(data, filterType, filterValue) {
    if (filterType === "none") {
        return removeChildrenFromLowestLevel(data);
    }

    if (filterType === "rolling" && filterValue !== "all") {
        return filterByRollingIndex(data, filterValue);
    }

    if (filterType === "index" && filterValue !== "all") {
        return filterByIndex(data, filterValue);
    }

    return data;
}

function removeChildrenFromLowestLevel(data) {
    const filteredData = JSON.parse(JSON.stringify(data));
    filteredData.children.forEach(nodeType => {
        nodeType.children.forEach(node => {
            delete node.children;
        });
    });
    return filteredData;
}

function filterByRollingIndex(data, filterValue) {
    const filteredData = JSON.parse(JSON.stringify(data));
    filteredData.children.forEach(nodeType => {
        nodeType.children.forEach(node => {
            node.children = node.children.filter(index => 
                rollingIndices[filterValue].includes(index.name)
            );
        });
        nodeType.children = nodeType.children.filter(node => node.children.length > 0);
    });
    filteredData.children = filteredData.children.filter(nodeType => nodeType.children.length > 0);
    return filteredData;
}

function filterByIndex(data, filterValue) {
    const filteredData = JSON.parse(JSON.stringify(data));
    filteredData.children.forEach(nodeType => {
        nodeType.children.forEach(node => {
            node.children = node.children.filter(index => index.name === filterValue);
        });
        nodeType.children = nodeType.children.filter(node => node.children.length > 0);
    });
    filteredData.children = filteredData.children.filter(nodeType => nodeType.children.length > 0);
    return filteredData;
}

function addRollingIndexNodesAndLinks(g, filterType, filterValue, width, height) {
    if (filterType === "rolling" && filterValue !== "all") {
        const indices = rollingIndices[filterValue];
        const x = width - 250;
        const y = height / 2;

        addRollingIndexNode(g, x, y, filterValue);
        addRollingIndexLinks(g, indices, x, y);
    }
}

function addRollingIndexNode(g, x, y, filterValue) {
    g.append("circle")
        .attr("cx", x)
        .attr("cy", y)
        .attr("r", 7)
        .style("fill", "#404080");

    g.append("text")
        .attr("x", x + 15)
        .attr("y", y)
        .attr("dy", ".35em")
        .text(`${filterValue} (${rollingIndicesSize[filterValue]} MB)`)
        .style("font-size", "12px")
        .style("font-weight", "bold");
}

function addRollingIndexLinks(g, indices, x, y) {
    g.selectAll(".node").each(function(d) {
        if (indices.includes(d.data.name)) {
            g.append("path")
                .attr("class", "rolling-link")
                .attr("d", d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x)
                    ({
                        source: {x: y, y: x},
                        target: {x: d.x, y: d.y}
                    }));
        }
    });
}
