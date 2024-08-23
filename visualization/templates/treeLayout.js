function createTreeLayout(root, g, width, height, nodeSpacing) {
    const treeLayout = d3.tree().size([height, width - 600]);
    
    // Custom layout function to ensure fixed spacing
    function customLayout(root) {
        treeLayout(root);
        root.eachBefore(node => {
            node.y = node.depth * 200;  // Fixed horizontal spacing
            if (node.parent) {
                node.x = node.parent.x + (node.parent.children.indexOf(node) - (node.parent.children.length - 1) / 2) * nodeSpacing;
            }
        });
        return root;
    }

    customLayout(root);

    // Create links
    g.selectAll(".link")
        .data(root.links())
        .enter().append("path")
        .attr("class", "link")
        .attr("d", d3.linkHorizontal()
            .x(d => d.y)
            .y(d => d.x));

    // Create nodes
    const node = g.selectAll(".node")
        .data(root.descendants())
        .enter().append("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.y},${d.x})`);

    // Add circles to nodes
    node.append("circle")
        .attr("r", 10)
        .style("fill", getNodeColor);

    // Add labels to nodes
    node.append("text")
        .attr("dy", ".35em")
        .attr("x", d => d.children ? -13 : 13)
        .style("text-anchor", d => d.children ? "end" : "start")
        .text(d => d.data.name)
        .style("font-size", d => d.depth === 3 ? "10px" : "12px");

    // Add node type counts
    node.filter(d => d.depth === 1)
        .append("text")
        .attr("dy", "1.5em")
        .attr("x", -13)
        .attr("text-anchor", "end")
        .attr("class", "node-type-count")
        .text(d => `(${d.children ? d.children.length : 0})`);

    // Add utilization bars for individual nodes
    addUtilizationBars(node.filter(d => d.depth === 2));
}
