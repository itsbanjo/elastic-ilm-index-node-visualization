function createForceLayout(root, g, width, height, nodeSpacing) {
    const simulation = d3.forceSimulation(root.descendants())
        .force("link", d3.forceLink(root.links()).id(d => d.id).distance(nodeSpacing))
        .force("charge", d3.forceManyBody().strength(-500))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .on("tick", ticked);

    // Create links
    const link = g.selectAll(".link")
        .data(root.links())
        .enter().append("line")
        .attr("class", "link");

    // Create nodes
    const node = g.selectAll(".node")
        .data(root.descendants())
        .enter().append("g")
        .attr("class", "node");

    // Add circles to nodes
    node.append("circle")
        .attr("r", 10)
        .style("fill", getNodeColor);

    // Add labels to nodes
    node.append("text")
        .attr("dy", ".35em")
        .attr("x", 13)
        .text(d => d.data.name)
        .style("font-size", d => d.depth === 3 ? "10px" : "12px");

    // Add node type counts
    node.filter(d => d.depth === 1)
        .append("text")
        .attr("dy", "1.5em")
        .attr("x", 13)
        .attr("class", "node-type-count")
        .text(d => `(${d.children ? d.children.length : 0})`);

    // Add utilization bars for individual nodes
    addUtilizationBars(node.filter(d => d.depth === 2));

    function ticked() {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("transform", d => `translate(${d.x},${d.y})`);
    }
}
