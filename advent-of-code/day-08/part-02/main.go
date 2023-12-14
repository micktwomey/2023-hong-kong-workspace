package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"runtime/pprof"
	"time"
)

type Node struct {
	Name string `json:"name"`
	L    string `json:"L"`
	R    string `json:"R"`
	A    bool   `json:"A"`
	Z    bool   `json:"Z"`
}

type Input struct {
	Steps []string         `json:"steps"`
	Nodes map[string]*Node `json:"nodes"`
}

// type GraphNode struct {
// 	Name string
// 	A    bool
// 	Z    bool
// 	L    *GraphNode
// 	R    *GraphNode
// }

var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to file")
var memprofile = flag.String("memprofile", "", "write memory profile to this file")
var input_filename = flag.String("input", "", "read input json from file")

// func build_graph(input *Input) GraphNode {
// 	// aaa_node := input.Nodes["AAA"]
// 	// var root_node = GraphNode{
// 	// 	Name: aaa_node.Name,
// 	// 	A:    string(aaa_node.Name[0]) == "A",
// 	// 	Z:    string(aaa_node.Name[2]) == "Z",
// 	// 	L:    nil,
// 	// 	R:    nil,
// 	// }
// 	var seen_nodes = map[string]GraphNode{}
// 	// seen_nodes["AAA"] = &root_node
// 	for _, node := range input.Nodes {
// 		graph_node := GraphNode{
// 			Name: node.Name,
// 			A:    string(node.Name[0]) == "A",
// 			Z:    string(node.Name[2]) == "Z",
// 			L:    nil,
// 			R:    nil,
// 		}
// 		seen_nodes[node.Name] = graph_node
// 		fmt.Printf("GraphNode: %+v", graph_node)
// 	}
// 	for _, graph_node := range seen_nodes {
// 		var l_graph_node = seen_nodes[input.Nodes[graph_node.Name].L]
// 		graph_node.L = &l_graph_node
// 		var r_graph_node = seen_nodes[input.Nodes[graph_node.Name].R]
// 		graph_node.R = &r_graph_node
// 	}
// 	root_node := seen_nodes["AAA"]
// 	return root_node
// }

// cycle forever over a list of strings
func cycle(iterable []string, ch chan string) {
	max := len(iterable)
	i := 0
	for {
		if i == max {
			i = 0
		}
		ch <- iterable[i]
		i++
	}
}

func solution(input Input) int {
	steps := -1

	// graph := build_graph(&input)
	// fmt.Printf("Graph: %+v\n", graph)
	// steps_channel := make(chan string)
	// go cycle(input.Steps, steps_channel)
	max_steps := len(input.Steps)
	current_step_i := 0
	var step string

	var current_node_names []string
	for _, node := range input.Nodes {
		if node.A {
			current_node_names = append(current_node_names, node.Name)
		}
	}
	desired_z_count := len(current_node_names)
	fmt.Printf("Desired Z node count: %d\n", desired_z_count)

	var z_count = 0
	var current_node *Node
	var next_node *Node
	var current_node_name string
	next_node_names := make([]string, desired_z_count)
	start := time.Now()
	for {
		if steps%1000000 == 0 {
			now := time.Now()
			elapsed := now.Sub(start)
			fmt.Printf("steps: %d z_count: %d current-nodes %+v elapsed: %s\n", steps, z_count, current_node_names, elapsed.String())
			start = now
			if steps > 1 && steps%(10000000) == 0 {
				return steps
			}
		}
		if desired_z_count == z_count {
			return steps
		}
		steps++
		// fmt.Printf("Step: %s - %d\n", step, steps)
		z_count = 0
		// clear(next_node_names)
		if current_step_i == max_steps {
			current_step_i = 0
		}
		step = input.Steps[current_step_i]

		for i := 0; i < desired_z_count; i++ {
			current_node_name = current_node_names[i]
			current_node = input.Nodes[current_node_name]
			if current_node.Z {
				z_count++
			}

			if step == "L" {
				next_node = input.Nodes[current_node.L]
			} else {
				next_node = input.Nodes[current_node.R]
			}
			next_node_names[i] = next_node.Name
		}
		current_node_names = next_node_names
	}

	return steps
}

func main() {
	flag.Parse()
	if *cpuprofile != "" {
		f, err := os.Create(*cpuprofile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}
	if *input_filename == "" {
		log.Fatal("Specify a filename to read with '-input filename'!")
	}
	fmt.Printf("Reading from %s\n", *input_filename)
	content, err := os.ReadFile(*input_filename)
	if err != nil {
		log.Fatal(err)
	}
	i := Input{}
	err = json.Unmarshal(content, &i)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%+v\n", i)

	solution_result := solution(i)
	fmt.Printf("solution: %d\n", solution_result)
	if *memprofile != "" {
		f, err := os.Create(*memprofile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.WriteHeapProfile(f)
		f.Close()
		return
	}
}
