function addTooltips(nodes) {
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    nodes.on("mouseover", function(event, d) {
        tooltip.transition()
            .duration(200)
            .style("opacity", .9);
        let tooltipContent = generateTooltipContent(d);
        tooltip.html(tooltipContent)
            .style("left", (event.pageX) + "px")
            .style("top", (event.pageY - 28) + "px");
    })
    .on("mouseout", function(d) {
        tooltip.transition()
            .duration(500)
            .style("opacity", 0);
    });
}

function generateTooltipContent(d) {
    let content = `${d.data.name}<br/>`;
    if (d.depth === 1) content += `Total Nodes: ${d.children ? d.children.length : 0}<br/>`;
    if (d.data.size) content += `Size: ${d.data.size} MB<br/>`;
    if (d.data.cpuUsage !== undefined) content += `CPU Usage: ${d.data.cpuUsage}%<br/>`;
    if (d.data.cpuFree !== undefined) content += `CPU Free: ${d.data.cpuFree}%<br/>`;
    if (d.data.memoryUsage !== undefined) content += `Memory Usage: ${d.data.memoryUsage}%<br/>`;
    if (d.data.memoryTotal !== undefined) content += `Memory Total: ${(d.data.memoryTotal / (1024 * 1024 * 1024)).toFixed(2)} GB<br/>`;
    if (d.data.diskUsage !== undefined) content += `Disk Usage: ${d.data.diskUsage}%<br/>`;
    if (d.data.diskTotal !== undefined) content += `Disk Total: ${(d.data.diskTotal / (1024 * 1024 * 1024)).toFixed(2)} GB<br/>`;
    
    if (d.data.memoryDetails) {
        content += addMemoryDetailsToTooltip(d.data.memoryDetails);
    }

    if (d.data.rollingIndex) {
        content += `Rolling Index: ${d.data.rollingIndex}<br/>`;
        content += `Total Size: ${rollingIndicesSize[d.data.rollingIndex]} MB<br/>`;
    }

    return content;
}

function addMemoryDetailsToTooltip(memDetails) {
    return `JVM Heap: ${(memDetails.jvmHeap / (1024 * 1024)).toFixed(2)} MB<br/>` +
           `Field Data Cache: ${(memDetails.fieldDataCache / (1024 * 1024)).toFixed(2)} MB<br/>` +
           `Query Cache: ${(memDetails.queryCache / (1024 * 1024)).toFixed(2)} MB<br/>` +
           `Segment Memory: ${(memDetails.segmentMemory / (1024 * 1024)).toFixed(2)} MB<br/>`;
}
