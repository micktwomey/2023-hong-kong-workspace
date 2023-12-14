package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"runtime/pprof"
)

type MappingDetail struct {
	Destination int `json:"destination"`
	Source      int `json:"source"`
	Count       int `json:"count"`
	MinSource   int `json:"min_source"`
	MaxSource   int `json:"max_source"`
}

type Mapping struct {
	Source      string           `json:"source"`
	Destination string           `json:"destination"`
	MinSource   int              `json:"min_source"`
	MaxSource   int              `json:"max_source"`
	Mappings    []*MappingDetail `json:"mappings"`
}

type SeedRange struct {
	Start int `json:"start"`
	End   int `json:"end"`
}

type Input struct {
	Seeds       []SeedRange       `json:"seeds"`
	Mappings    []Mapping         `json:"mappings"`
	NextMapping map[string]string `json:"next_mapping"`
}

func process_seed(seed int, input *Input, next_mappings []*Mapping) int {
	// fmt.Printf("process_seed %v mappings:%v\n", seed, next_mappings)
	var current_result = seed
	// for next_mapping := input.NextMapping["seed"]; next_mapping != ""; next_mapping = input.NextMapping[next_mapping] {
	// for _, next_mapping := range next_mappings {
	var current_mapping *Mapping
	var next_mapping *Mapping
	var mapping *MappingDetail
	for i := 0; i < len(next_mappings); i++ {
		next_mapping = next_mappings[i]

		// fmt.Printf("process_seed current_result %v next_mapping %+v\n", current_result, next_mapping)
		current_mapping = next_mapping
		if (current_result < current_mapping.MinSource) || (current_result > current_mapping.MaxSource) {
			// fmt.Printf("process_seed short circuit mapping %+v\n", next_mapping)
			continue
		}
		// for _, mapping := range current_mapping.Mappings {
		for j := 0; j < len(current_mapping.Mappings); j++ {
			mapping = current_mapping.Mappings[j]
			// fmt.Printf("process_seed evaluating current_result=%d against %+v\n", current_result, mapping)
			if (current_result >= mapping.MinSource) && (current_result <= mapping.MaxSource) {
				current_result = mapping.Destination + (current_result - mapping.Source)
				// fmt.Printf("process_seed mapping %+v -> %d\n", next_mapping, current_result)
				break
			}
		}
	}
	// fmt.Printf("process_seed seed %v -> result %v\n", seed, current_result)
	return current_result
}

func process_seed_range(seed_range *SeedRange, input *Input, next_mappings []*Mapping) int {
	fmt.Printf("process_seed_range %+v\n", seed_range)
	final_location := -1
	for seed := seed_range.Start; seed < (seed_range.Start + seed_range.End); seed++ {
		location := process_seed(seed, input, next_mappings)
		if final_location < 0 {
			final_location = location
		}
		if location < final_location {
			final_location = location
		}
		// locations = append(locations, location)
		if seed%10000000 == 0 {
			percent_complete := float32(seed-seed_range.Start) / float32(seed_range.End)
			fmt.Printf("process_seed_range %+v completed %0.2f%% location=%d final_location=%d\n", seed_range, percent_complete*100.0, location, final_location)
			// break
		}
	}
	fmt.Printf("process_seed_range %+v completed 100%% final_location=%d\n", seed_range, final_location)
	return final_location
}

// Convert the name -> next -> lookup to a flat list of mappings to iterate through
func flatten_next_mappings(input *Input) []*Mapping {
	next_mappings := make(map[string]Mapping)
	for _, mapping := range input.Mappings {
		fmt.Printf("Mapping: destination=%s mapping=%+v mapping=%v\n", mapping.Destination, mapping, &mapping)
		next_mappings[mapping.Destination] = mapping
		fmt.Printf("next_mappings[%s] = %v", mapping.Destination, mapping)
	}
	fmt.Printf("Next mappings: %+v\n", next_mappings)
	var mappings []*Mapping
	for next_mapping := input.NextMapping["seed"]; next_mapping != ""; next_mapping = input.NextMapping[next_mapping] {
		mapping := next_mappings[next_mapping]
		mappings = append(mappings, &mapping)
	}
	fmt.Printf("Flatter mappings: %+v %+v %+v\n", mappings, mappings[0], mappings[1])
	return mappings
}

func solution(input *Input) int {
	next_mappings := flatten_next_mappings(input)
	final_location := -1
	fmt.Printf("Seeds: %d\n", len(input.Seeds))
	var seed_range SeedRange
	// for _, seed_range := range input.Seeds {
	for i := 0; i < len(input.Seeds); i++ {
		seed_range = input.Seeds[i]
		fmt.Printf("process_seed_range %d/%d %+v\n", i+1, len(input.Seeds), seed_range)
		location := process_seed_range(&seed_range, input, next_mappings)
		if final_location < 0 {
			final_location = location
		}
		if location < final_location {
			final_location = location
		}
		fmt.Printf("process_seed_range %d/%d result=%v final_location=%d\n", i+1, len(input.Seeds), location, final_location)
		// break
	}
	fmt.Printf("solution final_locations %d\n", final_location)
	// return slices.Min(locations)
	return final_location
}

var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to file")
var memprofile = flag.String("memprofile", "", "write memory profile to this file")
var input_filename = flag.String("input", "", "read input json from file")

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
	// content, err := os.ReadFile("example.json")
	if err != nil {
		log.Fatal(err)
	}
	i := Input{}
	err = json.Unmarshal(content, &i)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%+v\n", i)

	location := solution(&i)
	fmt.Printf("location: %d\n", location)
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
