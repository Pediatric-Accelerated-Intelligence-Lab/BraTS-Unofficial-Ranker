import argparse
import os
import pandas as pd

# Name Factory
# set common name for each of the submissions

name_factory = {
    'INPT':{
        '3_geo': 'ensembling with pixel intensity geometric mean',
        '7': 'GM ensembling with median filter',
        '1': 'model 1',
        '2': 'model 2',
        '11': 'GEnnUNetPP_GEHE',
        '12':'MFnnUNetPP_MFHE'
    }
}


def rank_scores_multiple(*lists, error=False):
    """
    This function compares multiple lists of dice scores.
    The rank is determined by comparing each score at the same position across all lists.
    The highest score gets a rank of 1, the second highest gets 2, and so on.
    
    Args:
    *lists: Variable number of lists containing dice scores.
    
    Returns:
    list of lists: A list of lists containing ranks (1, 2, 3, ...) for each comparison in the same position.
    """
    if not lists:
        raise ValueError("At least one list is required.")

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
            if error:
                if score > current_score:
                    rank += 1
                    current_score = score
            else:
                if score < current_score:
                    rank += 1
                    current_score = score
            ranks[idx].append(rank)

    return ranks

def find_best_models(data, task, name_factory):
    # sample_model = next(iter(data.values()))
    # regions = set()
    # for key in sample_model.keys():
    #     if key.startswith('LesionWise_Dice_'):
    #         region = key.split('LesionWise_Dice_')[1]
    #         regions.add(region)
    # regions = sorted(list(regions))
    # print()
    # print(f'The {task} task has following regions:', regions)
    # print()   
    # best_models = {region: None for region in regions}
    # best_scores = {region: float('inf') for region in regions}

    overall_scores = {}
    for model, scores in data.items():
        overall_scores[model] = (scores[f'SSIM'] + scores[f'PSNR'] + scores[f'MSE']) / 3

    best_overall_model = min(overall_scores, key=overall_scores.get)
    sorted_models = sorted(overall_scores.items(), key=lambda item: item[1])

    # for region in regions:
    #     model = best_models[region].split('/')[-1][:-4]
    #     print(f"Best model for {region}: '{model}:{name_factory[task][model]}' with mean score {round(best_scores[region],4)}")

    print()
    best_overall_model_csv = best_overall_model.split('/')[-1][:-4]
    print(f"Best overall model: '{best_overall_model_csv}:{name_factory[task][best_overall_model_csv]}' with mean score {round(overall_scores[best_overall_model],4)}")
    print()
    print("Top 10 models:\n")
    for i, (model, score) in enumerate(sorted_models[:10], start=1):
        model = model.split('/')[-1][:-4]
        print(f"{i}. {model}:{name_factory[task][model]} with mean score {round(score,4)}")
        

def get_rank(task, name_factory):
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
        if 'MSE' in col:
            ranks = rank_scores_multiple(*scores, error=True)
        elif 'PSNR' in col:
            ranks = rank_scores_multiple(*scores)
        elif 'SSIM' in col:
            ranks = rank_scores_multiple(*scores)
        else:
            continue
        
        for i, df in enumerate(dfs):
            df[col+'_rank'] = ranks[i]
            rank_mean[all_submissions_path[i]][col]=sum(ranks[i])/len(ranks[i])
            
    #print(rank_mean)
    find_best_models(rank_mean, task, name_factory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get rank of submissions')
    parser.add_argument('--task', required=True, help='task name')
    args = parser.parse_args()

    
    get_rank(args.task, name_factory)
