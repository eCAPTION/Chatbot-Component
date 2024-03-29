from dotenv import load_dotenv
import os
from linetimer import CodeTimer
import requests

load_dotenv()

huggingface_access_token = os.getenv("HUGGING_FACE_ACCESS_TOKEN")
instruction_type_api_url = os.getenv("INSTRUCTION_TYPE_API_URL")
target_element_add_api_url = os.getenv("TARGET_ELEMENT_NEW_API_URL")
target_location_add_api_url = os.getenv("TARGET_LOCATION_NEW_API_URL")
target_element_delete_api_url = os.getenv("TARGET_ELEMENT_NEW_DELETE_API_URL")
infographic_section_api_url = os.getenv("INFOGRAPHIC_SECTION_NEW_API_URL")
target_element_move_api_url = os.getenv("TARGET_ELEMENT_NEW_MOVE_API_URL")
reference_element_move_api_url = os.getenv("REFERENCE_ELEMENT_NEW_MOVE_API_URL")
direction_move_api_url = os.getenv("DIRECTION_NEW_MOVE_API_URL")


def identify_instruction_type(instruction):
    with CodeTimer('Identify Instruction Type', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(instruction_type_api_url, headers=headers, json=payload)
            return response.json()

        prompt_instruction_type = f'Given the following instruction to modify an infographic: "{instruction}" Identify the type of operation specified in the instruction: ADD/DELETE/EDIT/MOVE.'
        output_instruction_type = query({
            "inputs": prompt_instruction_type,
            "options": {
                "wait_for_model": True
            },
        })

    instruction_type = output_instruction_type[0]['generated_text']
    return instruction_type


def identify_target_element_add(instruction):
    with CodeTimer('Identify Target Element', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(target_element_add_api_url, headers=headers, json=payload)
            return response.json()

        prompt_target_element = f'Given the instruction, ({instruction}) Output the specific content or element that is added to the infographic. Ensure that the answer does not include the target location of the element or text.'
        output_target_element = query({
            "inputs": prompt_target_element,
            "options": {
                "wait_for_model": True
            },
        })

    target_element = output_target_element[0]['generated_text']
    return target_element


def identify_target_location_add(instruction):
    with CodeTimer('Identify Target Location', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(target_location_add_api_url, headers=headers, json=payload)
            return response.json()

        prompt_target_location = f'Identify the target location in the existing infographic where the new element will be added next to based on the following user instruction: {instruction}'
        output_target_location = query({
            "inputs": prompt_target_location,
            "options": {
                "wait_for_model": True
            },
        })

    target_location = output_target_location[0]['generated_text']
    return target_location


def identify_target_element_delete(instruction):
    with CodeTimer('Identify Target Element', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(target_element_delete_api_url, headers=headers, json=payload)
            return response.json()

        prompt_target_element = f'Given the instruction, ({instruction}) Output the specific content or element that is deleted from the infographic.'
        output_target_element = query({
            "inputs": prompt_target_element,
            "options": {
                "wait_for_model": True
            },
        })

    target_element = output_target_element[0]['generated_text']
    return target_element


def identify_infographic_section_new(location):
    with CodeTimer('Identify Infographic Section', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(infographic_section_api_url, headers=headers, json=payload)
            return response.json()

        infographic_sections = "The infographic comprises a 'Header' section featuring the title of the article. The 'Number of Shares' section displays the numerical count of shares of this infographic. The 'Vote on Reliability' section presents a diagram reflecting user opinions and votes on the news article's reliability. The 'Related Facts' section lists statements and relevant facts related to the article, while the 'Latest Comments' section displays the list of comments submitted by the users. The 'Knowledge Graph Summaries' section showcases sentiments towards various entities mentioned in the news through a knowledge graph, which is a graph representing semantic relationships between entities. Lastly, 'Similar Articles' provides a list of similar articles with diverse viewpoints, each accompanied by a QR code, header, and a brief summary."
        task = f'Based on the context, which infographic section (Header, Number of Shares, Vote on Reliability, Related Facts, Latest Comments, Knowledge Graph Summaries, Similar Articles) does "{location}" belong to?'
        output_infographic_section = query({
            "inputs": {
                "question": task,
                "context": infographic_sections
            },
            "options": {
                "wait_for_model": True
            },
        })

    return remove_quotes_again(remove_quotes(output_infographic_section['answer']))


def remove_quotes(string):
    if string.startswith(' \'') and string.endswith('\''):
        return string[2:-1]
    else:
        return string


def remove_quotes_again(string):
    opening_index = string.find('\'')
    closing_index = string.rfind('\'')
    if opening_index == -1 or closing_index == -1 or opening_index > closing_index:
        return string
    else:
        return string[opening_index + 1:closing_index]


def identify_target_element_move(instruction):
    with CodeTimer('Identify Target Element', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(target_element_move_api_url, headers=headers, json=payload)
            return response.json()

        prompt_target_element = f'Given the instruction, ({instruction}) Output the target element the user wants to move in this infographic.'
        output_target_element = query({
            "inputs": prompt_target_element,
            "options": {
                "wait_for_model": True
            },
        })

    target_element = output_target_element[0]['generated_text']
    return target_element


def identify_reference_element_move(instruction):
    with CodeTimer('Identify Reference Element', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(reference_element_move_api_url, headers=headers, json=payload)
            return response.json()

        prompt_reference_element = f'Given the instruction, ({instruction}) Output the reference element the user wants to position the target element in relation to.'
        output_reference_element = query({
            "inputs": prompt_reference_element,
            "options": {
                "wait_for_model": True
            },
        })

    reference_element = output_reference_element[0]['generated_text']
    return reference_element


def identify_direction_move(instruction):
    with CodeTimer('Identify Direction', unit='s'):
        headers = {"Authorization": f"Bearer {huggingface_access_token}"}

        def query(payload):
            response = requests.post(direction_move_api_url, headers=headers, json=payload)
            return response.json()

        prompt_direction = f'Given the instruction, ({instruction}) Identify the direction in which the user wants to move the target element relative to the reference element: above/below/left/right'
        output_direction = query({
            "inputs": prompt_direction,
            "options": {
                "wait_for_model": True
            },
        })

    direction = output_direction[0]['generated_text']
    return direction


def generate_intermediate_representation(instruction):
    instruction_type = identify_instruction_type(instruction)
    intermediate_representation = {}
    if instruction_type == 'ADD':
        target_element = identify_target_element_add(instruction)
        target_section = identify_infographic_section_new(target_element)
        # target_location = identify_target_location_add(instruction)
        # infographic_section = identify_infographic_section_new(target_location)
        intermediate_representation = {
            'instruction_type': instruction_type,
            'target_element': target_section,
            # 'infographic_section': infographic_section,
        }
    elif instruction_type == 'DELETE':
        target_element = identify_target_element_delete(instruction)
        infographic_section = identify_infographic_section_new(target_element)
        intermediate_representation = {
            'instruction_type': instruction_type,
            'infographic_section': infographic_section,
        }
    elif instruction_type == 'MOVE':
        target_element = identify_target_element_move(instruction)
        target_infographic_section = identify_infographic_section_new(target_element)
        reference_element = identify_reference_element_move(instruction)
        reference_infographic_section = identify_infographic_section_new(reference_element)
        direction = identify_direction_move(instruction)
        if direction == 'above':
            direction = 'top'
        elif direction == 'below':
            direction = 'bottom'
        intermediate_representation = {
            'instruction_type': instruction_type,
            'target_section': target_infographic_section,
            'reference_section': reference_infographic_section,
            'direction': direction
        }
    return intermediate_representation

