console.log("In js file!")

function updateChart(nums) {
    svg.selectAll("path").remove()
    // Add X axis --> it is a date format (changed to reflect crazyflie pos)
    const x = d3.scaleLinear()
      .domain([-3, 3])
      .range([ -width, width ]);
    //svg.append("g")
    //  .attr("transform", `translate(${width/2}, ${height/2})`)
    //  .style('opacity', 0.4)
    //  .call(d3.axisBottom(x));

    // Add Y axis (changed to reflect likely space for crazyflie)
    const y = d3.scaleLinear()
      .domain([-3, 3])
      .range([ height, 0 ]);
    //svg.append("g")
    //  .attr("transform", `translate(${width/2}, 0)`)
    //  .style('opacity', 0.0)
    //  .call(d3.axisLeft(y));
    svg.append("path")
      .datum(nums)
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("transform", `translate(${width/2}, 0)`)
      .attr("d", d3.line()
        .x(function(d) { return x(d[0]) })
        .y(function(d) { return y(d[1]) })
        )

}
  // Note: mostly adapted from "Basic line chart" d3js example: https://www.d3-graph-gallery.com/graph/line_basic.html
  // set the dimensions and margins of the graph
const margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 600 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

  // append the svg object to the body of the page
const svg = d3.select("#cfviz")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  let nums = [[0, 1], [.1, 1], [.2, 1]];
  let nums2 = [[0, 2], [.1, 2], [.2, 2]];
console.log("Made nums const!")
  //Read the data
d3.csv("https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/3_TwoNumOrdered_comma.csv",

  // Change to some static variables for the time being
  function(d){
    //return { date : d3.timeParse("%Y-%m-%d")(d.date), value : d.value }
    return { x: nums.map((arr) => { return arr[0] }), vx : nums.map((arr) => {return arr[1]}) }
  }).then(

  // Now I can use this dataset:
  function(data) {

    let arr = {x : nums.map((arr) => { return arr[0] }), vx : nums.map((arr) => {return arr[1]})}
    //var path = d3.select("#cfviz").select("g")
    //console.log(path)
    //console.log("^Path")
      //.domain(d3.extent(data, function(d) { return d; }))
    // Add X axis --> it is a date format (changed to reflect crazyflie pos)
    const x = d3.scaleLinear()
      .domain([-3, 3])
      .range([ -width, width ]);
    // Append the created linear scale to "g" component of svg
    svg.append("g")
      .attr("transform", `translate(${width/2}, ${height/2})`)
      .style('opacity', 0.4)
      .call(d3.axisBottom(x));
    // Add X axis label:
    svg.append("text")
        .attr("text-anchor", "end")
        .attr("x", width)
        .attr("y", height + margin.top + 20)
        .text("X Position");

      //.domain([-d3.max(data, function(d) { return +d; }), d3.max(data, function(d) { return +d; })])
    // Add Y axis (changed to reflect likely space for crazyflie)
    const y = d3.scaleLinear()
      .domain([-3, 3])
      .range([ height, 0 ]);

    // As before, but append newly created y axis
    svg.append("g")
      .attr("transform", `translate(${width/2}, 0)`)
      .style('opacity', 0.4)
      .call(d3.axisLeft(y));

    // Add the line
    svg.append("path") // appends the path element to svg directly?
      .datum(nums)
      .attr("id", "path")
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("transform", `translate(${width/2}, 0)`)
      .attr("d", d3.line()
        .x(function(d) { return x(d[0]) })
        .y(function(d) { return y(d[1]) })
        )
    nums = nums2
    console.log(d3.select("#path").data())
    console.log(svg)
    console.log("Nums")
    console.log(nums)
    axios.get('/trajectory').then((resp) => {
      console.log("Axios")
      console.log(resp.data.state)
    })
    //setInterval(function() { 
    //  console.log("Changing")
    //  nums = [...Array(3).fill([...Array(2)])].map(() => [Math.floor(Math.random() * 2), Math.floor(Math.random() * 3)])
    //  updateChart(nums)
    //  console.log(nums)
    //}, 5000);
    setInterval(function() { 
      axios.get('/trajectory').then( (resp) => {
        updateChart(resp.data.state)
      }).catch( (err) => { console.log("Server down") })
    }, 100);
})

