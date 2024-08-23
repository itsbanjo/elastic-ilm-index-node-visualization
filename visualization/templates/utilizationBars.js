function addUtilizationBars(nodes) {
    nodes.append("g")
        .attr("transform", "translate(20, -30)")
        .call(g => {
            const barWidth = 60;
            const barHeight = 5;
            const metrics = [
                {name: "CPU", key: "cpuUsage", color: "#4CAF50"},
                {name: "Memory", key: "memoryUsage", color: "#2196F3"},
                {name: "Disk", key: "diskUsage", color: "#FFC107"}
            ];

            metrics.forEach((metric, i) => {
                addUtilizationBar(g, metric, i, barWidth, barHeight);
            });
        });
}

function addUtilizationBar(g, metric, index, barWidth, barHeight) {
    g.append("rect")
        .attr("y", index * (barHeight + 2))
        .attr("width", barWidth)
        .attr("height", barHeight)
        .attr("class", "utilization-background");

    g.append("rect")
        .attr("y", index * (barHeight + 2))
        .attr("width", d => (d.data[metric.key] / 100) * barWidth)
        .attr("height", barHeight)
        .attr("fill", metric.color);

    g.append("text")
        .attr("x", barWidth + 5)
        .attr("y", index * (barHeight + 2) + barHeight)
        .text(d => `${metric.name}: ${d.data[metric.key]}%`)
        .style("font-size", "8px");
}
