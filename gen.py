from sdk import solve, find_candidates, print_log_fn, copy_sdk, get_free_cells
from random import choice

def log_mute(text, depth = 0):
	return

def all_set_cells(sudoku):
	return [(i, j) for j in range(9) for i in range(9) if sudoku[i][j]]

def gen_sdk():
	sudoku = [[None for j in range(9)] for i in range(9)]
	while True:
#		(i, j) = choice(get_free_cells(sudoku))
		
		copy = copy_sdk(sudoku)
#		solve(copy, log_mute, 2, False, False)
		free_cells = get_free_cells(copy)
		candidates_map = find_candidates(copy)
		max_length = max([len(candidates_map[i][j]) for (i, j) in free_cells])
		max_cells = [(i, j) for (i, j) in free_cells if len(candidates_map[i][j]) == max_length]
		(i, j) = choice(max_cells)
		
		value = choice(find_candidates(sudoku)[i][j])
		copy = copy_sdk(sudoku)
		copy[i][j] = value
		nr_solutions = len(solve(copy, log_mute, 2, False))
#		print('put {} in {} yields {}'.format(value, (i+1, j+1), solutions))
		if nr_solutions == 1:
			return copy
		elif nr_solutions > 1:
			sudoku = copy

def remove_redundand(sudoku):
	for (i, j) in all_set_cells(sudoku):
		copy = copy_sdk(sudoku)
		copy[i][j] = None
		solutions = solve(copy, log_mute, 2)
		if len(solutions) == 1:
#			print('removing {}'.format((i+1, j+1)))
			sudoku = copy
	return sudoku

def main():
	sudoku = gen_sdk()
	sudoku = remove_redundand(sudoku)
	print('\n'.join([''.join([str(sudoku[i][j]) if sudoku[i][j] else ' ' for j in range(9)]) for i in range(9)]))
	solve(sudoku, print_log_fn, 2)

if __name__ == "__main__":
	main()
