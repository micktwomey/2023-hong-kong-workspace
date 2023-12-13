package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
)

type Mapping struct {
	Source      string `json:"source"`
	Destination string `json:"destination"`
	MinSource   int    `json:"min_source"`
	MaxSource   int    `json:"max_source"`
	Mappings    []struct {
		Destination int `json:"destination"`
		Source      int `json:"source"`
		Count       int `json:"count"`
		MinSource   int `json:"min_source"`
		MaxSource   int `json:"max_source"`
	}
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

func process_seed(seed int, input Input, next_mappings map[string]Mapping) int {
	fmt.Printf("process_seed %v\n", seed)
	var current_result = seed
	for next_mapping := input.NextMapping["seed"]; next_mapping != ""; next_mapping = input.NextMapping[next_mapping] {
		fmt.Printf("process_seed current_result %v next_mapping %s\n", current_result, next_mapping)
		current_mapping := next_mappings[next_mapping]
		if (current_result < current_mapping.MinSource) || (current_result >= current_mapping.MaxSource) {
			fmt.Printf("process_seed short circuit mapping %s\n", next_mapping)
			continue
		}
		for _, mapping := range current_mapping.Mappings {
			if (current_result >= mapping.MinSource) && (current_result < mapping.MaxSource) {
				current_result = mapping.Destination + (current_result - mapping.Source)
				fmt.Printf("process_seed mapping %s -> %d\n", next_mapping, current_result)
				break
			}
		}
	}
	fmt.Printf("process_seed seed %v ->  %v\n", seed, current_result)
	return current_result
}

func process_seed_range(seed_range SeedRange, input Input, next_mappings map[string]Mapping) int {
	fmt.Printf("process_seed_range %+v\n", seed_range)
	var location int = 0
	for seed := seed_range.Start; seed < (seed_range.Start + seed_range.End); seed++ {
		location = process_seed(seed, input, next_mappings)
		if seed%1000 == 0 {
			break
		}
	}
	return location
}

func solution(input Input) {
	var next_mappings = map[string]Mapping{}
	for _, mapping := range input.Mappings {
		next_mappings[mapping.Destination] = mapping
	}
	for _, seed_range := range input.Seeds {
		result := process_seed_range(seed_range, input, next_mappings)
		fmt.Printf("process_seed_range result %+v\n", result)
	}
}

func main() {
	content, err := os.ReadFile("input.json")
	if err != nil {
		log.Fatal(err)
	}
	i := Input{}
	err = json.Unmarshal(content, &i)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("%+v\n", i)

	solution(i)
}
