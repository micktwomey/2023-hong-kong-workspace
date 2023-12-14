package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"runtime/pprof"
)

type Race struct {
	Time     int `json:"time"`
	Distance int `json:"distance"`
}

type Input []Race

var startat = flag.Int("startat", 0, "where to start evaluating?")
var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to file")
var memprofile = flag.String("memprofile", "", "write memory profile to this file")
var input_filename = flag.String("input", "", "read input json from file")

func solution(input Input) int {
	held := 0
	if *startat > 0 {
		held = *startat
	}
	total := 1
	for i, race := range input {
		fmt.Printf("%d race: %v\n", i, race)
		wins := 0
		for held := held; held <= race.Time; held++ {
			remaining_time := race.Time - held
			distance_multiplier := remaining_time
			// if held > 0 {
			// 	distance_multiplier = remaining_time % held
			// }
			travelled := held * distance_multiplier
			beat_record := travelled > race.Distance
			if beat_record {
				wins++
			}
			if held%10000000 == 0 {
				fmt.Printf("race: %v held: %d remaining: %d distance_multiplier: %d travelled: %d beat_record? %v wins: %d\n", race, held, remaining_time, distance_multiplier, travelled, beat_record, wins)
			}
		}
		total = total * wins
	}
	return total
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
