import argparse
import os
import pandas as pd
import numpy as np

# Name Factory
# set common name for each of the submissions
name_factory = {
    'SSA':{
        '9752810': 'model',
        '9754422': 'model + PP_cc',
        '9754423': 'model + PP_cc + PP_lblredef',

    },
    'DUMMY_TASK':{
        'CSV1NAME': 'DESCRIPTION1',
        'CSV2NAME': 'DESCRIPTION2',
        'CSV3NAME': 'DESCRIPTION3',
    }
}

def rank_scores_multiple(*lists):
    """
    This function compares multiple lists of dice scores.
    The rank is determined by comparing each score at the same position across all lists.
    The highest score gets a rank of 1, the second highest gets 2, and so on.
    
    Args:
    *lists: Variable number of lists containing dice scores.
    
    Returns:
    list of lists: A list of lists containing ranks (1, 2, 3, ...) for each comparison in the same position.
    """

    num_lists = len(lists)
    list_length = len(lists[0])

    # Check if all lists have the same length
    for lst in lists:
        if len(lst) != list_length:
            raise ValueError("All lists must have the same length.")

    ranks = [[] for _ in range(num_lists)]

    for i in range(list_length):
        scores = [(lst[i], idx) for idx, lst in enumerate(lists)]
        sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)
        rank = 1
        current_score = sorted_scores[0][0]

        for score, idx in sorted_scores:
            if score < current_score:
                rank += 1
                current_score = score
            ranks[idx].append(rank)

    return ranks

def find_best_models(data, task, name_factory):
    """ This function finds the best models for each region based on the scores provided in the data.
    It calculates the mean score for each region and identifies the best model for each region.
    It also calculates the overall mean score for each model across all regions and identifies the best overall model.
    Finally, it prints the best models for each region and the best overall model, along with their mean scores.
    It also prints the top 10 models based on their overall mean scores.        

    Args:
        data (dict): A dictionary where keys are model names and values are dictionaries of scores for each region.
        task (str): The name of the task for which the models are being evaluated.
        name_factory (dict): A dictionary mapping model names to their common names.
    """
    print(f'Analyzing {len(data)} models for task {task}')
    print()
    sample_model = next(iter(data.values()))
    regions = set()
    for key in sample_model.keys():
        if key.startswith('LesionWise_Dice_'):
            region = key.split('LesionWise_Dice_')[1]
            regions.add(region)
    regions = sorted(list(regions))
    print()
    print(f'The {task} task has following regions:', regions)
    print()   
    best_models = {region: None for region in regions}
    best_scores = {region: float('inf') for region in regions}

    overall_scores = {}
    for model, scores in data.items():
        total_mean_score = 0
        for region in regions:
            mean_score = (scores[f'LesionWise_Dice_{region}'] + scores[f'LesionWise_NSD_1.0_{region}'] + scores[f'LesionWise_NSD_0.5_{region}']) / 3
            total_mean_score += mean_score
            if mean_score < best_scores[region]:
                best_scores[region] = mean_score
                best_models[region] = model
        overall_scores[model] = total_mean_score / len(regions)

    best_overall_model = min(overall_scores, key=overall_scores.get)
    sorted_models = sorted(overall_scores.items(), key=lambda item: item[1])

    for region in regions:
        model = best_models[region].split('/')[-1][:-4]
        print(f"Best model for {region}: '{model}:{name_factory[task][model]}' with mean score {round(best_scores[region],4)}")

    print()
    best_overall_model_csv = best_overall_model.split('/')[-1][:-4]
    print(f"Best overall model: '{best_overall_model_csv}:{name_factory[task][best_overall_model_csv]}' with mean score {round(overall_scores[best_overall_model],4)}")
    print()
    print("Top 10 models:\n")
    for i, (model, score) in enumerate(sorted_models[:10], start=1):
        model = model.split('/')[-1][:-4]
        print(f"{i}. {model}:{name_factory[task][model]} with mean score {round(score,4)}")
        

def get_rank(task, name_factory):
    """ This function retrieves the rank of submissions for a given task.
    It reads the CSV files for each submission, calculates the ranks based on the scores,
    and then finds the best models for each region and overall.
    
    Args:        
        task (str): The name of the task for which the ranks are to be calculated.
        name_factory (dict): A dictionary mapping submission IDs to their common names.
    """
    # get the list of submissions for the task
    submissions = name_factory[task]
    all_submissions_path = [os.path.join(task, sub_id+'.csv') for sub_id, _ in submissions.items()]
    print(f'Analyzing {len(all_submissions_path)} submissions for task {task}')
    print(all_submissions_path)
    print()

    # get df for each submission
    dfs = []
    for sub_path in all_submissions_path:
        df = pd.read_csv(sub_path)
        df = df.loc[:, ~df.columns.str.startswith('Num')]
        dfs.append(df)

    # for each of the columns of the df, get the rank of the submission
    rank_mean = {sub: {}for sub in all_submissions_path}

    for col in dfs[0].columns:
        
        scores = [df[col].to_list() for df in dfs]
        if 'Dice' in col:
            ranks = rank_scores_multiple(*scores)
        elif 'NSD' in col:
            ranks = rank_scores_multiple(*scores)
        else:
            continue
        
        for i, df in enumerate(dfs):
            df[col+'_rank'] = ranks[i]
            rank_mean[all_submissions_path[i]][col]=sum(ranks[i])/len(ranks[i])
            
    #print(rank_mean)
    find_best_models(rank_mean, task, name_factory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get rank metrics of the validation submissions')
    parser.add_argument('--task', required=True, help='task name')
    args = parser.parse_args()
    get_rank(args.task, name_factory)