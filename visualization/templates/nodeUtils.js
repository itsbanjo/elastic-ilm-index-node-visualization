function getNodeColor(d) {
    if (d.depth === 0) return "#69b3a2";
    if (d.depth === 1) return "#404080";
    if (d.depth === 2) {
        return d.parent.data.name === "Hot Nodes" ? "#ff4136" :
               d.parent.data.name === "Warm Nodes" ? "#ff851b" :
               d.parent.data.name === "Cold Nodes" ? "#0074d9" :
               "#b10dc9";
    }
    return d.data.rollingIndex ? "#ffd700" : "#aaa";
}

function addNodeTypeCount(node) {
    node.filter(d => d.depth === 1)
        .append("text")
        .attr("dy", "1.5em")
        .attr("x", d => d.children ? -13 : 13)
        .attr("text-anchor", d => d.children ? "end" : "start")
        .attr("class", "node-type-count")
        .text(d => `(${d.children ? d.children.length : 0})`);
}
